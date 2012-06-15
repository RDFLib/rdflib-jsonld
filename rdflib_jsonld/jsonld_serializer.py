# -*- coding: utf-8 -*-
"""
This serialiser will output an RDF Graph as a JSON-LD formatted document. See:

    http://json-ld.org/

Example usage::

    >>> from rdflib import Graph, plugin
    >>> from rdflib.serializer import Serializer

    >>> testrdf = '''
    ... @prefix dc: <http://purl.org/dc/terms/> .
    ... <http://example.org/about>
    ...     dc:title "Someone's Homepage"@en .
    ... '''

    >>> g = Graph().parse(data=testrdf, format='n3')

    >>> print(g.serialize(format='json-ld', indent=4))
    {
        "@context": {
            "dc": "http://purl.org/dc/terms/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
        },
        "@id": "http://example.org/about",
        "dc:title": {
            "@language": "en",
            "@literal": "Someone's Homepage"
        }
    }

"""

# NOTE: This code writes the entire JSON object into memory before serialising,
# but we should consider streaming the output to deal with arbitrarily large
# graphs.

import warnings

from rdflib.serializer import Serializer
from rdflib.term import URIRef, Literal, BNode
from rdflib.namespace import RDF, XSD

from ldcontext import Context, ID_KEY, LIST_KEY, SET_KEY
from ldcontext import json

__all__ = ['JsonLDSerializer', 'to_tree']

PLAIN_LITERAL_TYPES = set([XSD.integer, XSD.float, XSD.double, XSD.decimal,
        XSD.boolean, XSD.string])


class JsonLDSerializer(Serializer):
    def __init__(self, store):
        super(JsonLDSerializer, self).__init__(store)

    def serialize(self, stream, base=None, encoding=None, **kwargs):
        """
        @@ TODO: add docstring describing args and returned value type
        """
        encoding = encoding or 'utf-8'
        if encoding not in ('utf-8', 'utf-16'):
            warnings.warn("JSON should be encoded as unicode. " +
                    "Given encoding was: %s" % encoding)

        context_data = kwargs.get('context')
        generate_compact = kwargs.get('compact', True)
        indent = kwargs.get('indent', 2)
        separators = (',', ': ')
        sort_keys = True
        tree = to_tree(self.store, context_data, base,
                generate_compact=generate_compact)
        data = json.dumps(tree, indent=indent, separators=separators,
                sort_keys=sort_keys)

        stream.write(data.encode(encoding, 'replace'))


def to_tree(graph, context_data=None, base=None, generate_compact=True):
    """
    @@ TODO: add docstring describing args and returned value type
    """

    tree = {}

    # TODO: Check which prefixes are actually used when creating curies and add
    # incrementally. (Use rdflib features for this, e.g. RecursiveSerializer?)
    if not context_data:
        if generate_compact:
            context_data = dict((pfx, unicode(ns))
                    for (pfx, ns) in graph.namespaces() if pfx and
                    unicode(ns) != u"http://www.w3.org/XML/1998/namespace")

    if isinstance(context_data, Context):
            context = context_data
            context_data = context.to_dict()
    else:
        context = Context(context_data)

    if context_data:
        tree[context.context_key] = context_data

    nodes = []

    state = (graph, context, base)

    # TODO: framing/CBD-with-startnode...
    for s in set(graph.subjects()):
        # only unreferenced.. TODO: not if more than one ref!
        if isinstance(s, URIRef) or not any(graph.subjects(None, s)):
            current = _subject_to_node(state, s)
            nodes.append(current)

    if len(nodes) == 1:
        tree.update(nodes[0])
    else:
        tree[context.graph_key] = nodes

    return tree


def _subject_to_node(state, s):
    (graph, context, base) = state
    current = {}
    if isinstance(s, URIRef):
        current[context.id_key] = context.shrink(s)
    p_objs = {}
    for p, o in graph.predicate_objects(s):
        objs = p_objs.setdefault(p, [])
        objs.append(o)
    for p, objs in p_objs.items():
        p_key, node = _key_and_node(state, p, objs)
        current[p_key] = node

    return current


def _key_and_node(state, p, objs):
    p_key, many, repr_value = _handles_for_property(state, p, objs)
    node = None
    if not many:
        node = repr_value(objs[0])
    else:
        node = [repr_value(o) for o in objs]
    return p_key, node


def _handles_for_property(state, p, objs):
    (graph, context, base) = state
    repr_value = lambda o: _to_raw_value(state, o)
    # context.shrink(o) if isinstance(o, URIRef) else o # py2.4 compat
    iri_to_id = (lambda o:
            isinstance(o, URIRef) and context.shrink(o) or o)
    term = context.get_term(unicode(p))
    if term:
        p_key = term.key
        if term.container == SET_KEY:
            many = True
        else:
            many = not len(objs) == 1
        if term.coercion:
            if term.coercion == ID_KEY:
                repr_value = iri_to_id
            else:
                #o if unicode(o.datatype) == term.coercion
                #        else _to_raw_value(state, o)
                # for py24:
                repr_value = (lambda o: (
                        unicode(o.datatype) == term.coercion) \
                        and o \
                        or _to_raw_value(state, o))
    else:
        if not term and p == RDF.type:
            repr_value = iri_to_id
        p_key = context.shrink(p)
        many = not len(objs) == 1

    # TODO: working, but in need of refactoring...
    if term and term.container == LIST_KEY:
        wrapped_repr = repr_value
        repr_value = lambda o: wrapped_repr(o)[context.list_key]

    return p_key, many, repr_value


def _to_raw_value(state, o):
    (graph, context, base) = state
    coll = _to_collection(state, o)
    if coll is not None:
        return coll
    elif isinstance(o, BNode):
        return _subject_to_node(state, o)
    elif isinstance(o, URIRef):
        return {context.id_key: context.shrink(o)}
    elif isinstance(o, Literal):
        v = o
        if o.language and o.language != context.lang:
            return {context.lang_key: o.language,
                    context.literal_key: v}
        elif o.datatype:
             #https://github.com/RDFLib/rdflib-jsonld/issues/4
             #serialize data type regardless
             #if o.datatype in PLAIN_LITERAL_TYPES:
             #    return o.toPython()
            return {context.type_key: context.shrink(o.datatype),
                    context.literal_key: v}
        else:
            return v


def _to_collection(state, subj):
    (graph, context, base) = state
    if subj == RDF.nil:
        return {context.list_key: []}
    elif (subj, RDF.first, None) in graph:
        return {context.list_key: list(_to_raw_value(state, o)
                                for o in graph.items(subj))}
    else:
        return None

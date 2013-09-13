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
        "@id": "http://example.org/about",
        "http://purl.org/dc/terms/title": [
            {
                "@language": "en",
                "@value": "Someone's Homepage"
            }
        ]
    }

"""

# NOTE: This code writes the entire JSON object into memory before serialising,
# but we should consider streaming the output to deal with arbitrarily large
# graphs.

import warnings

from rdflib.serializer import Serializer
from rdflib.graph import Graph
from rdflib.term import URIRef, Literal, BNode
from rdflib.namespace import RDF, XSD

from .context import Context
from .util import json
from .keys import CONTEXT, GRAPH, ID, LIST, SET

__all__ = ['JsonLDSerializer', 'from_rdf']


PLAIN_LITERAL_TYPES = set([XSD.integer, XSD.float, XSD.double, XSD.decimal,
                           XSD.boolean, XSD.string])


class JsonLDSerializer(Serializer):
    def __init__(self, store):
        super(JsonLDSerializer, self).__init__(store)

    def serialize(self, stream, base=None, encoding=None, **kwargs):
        # TODO: docstring w. args and return value
        encoding = encoding or 'utf-8'
        if encoding not in ('utf-8', 'utf-16'):
            warnings.warn("JSON should be encoded as unicode. " +
                          "Given encoding was: %s" % encoding)

        context_data = kwargs.get('context')
        auto_compact = kwargs.get('auto_compact', False)
        indent = kwargs.get('indent', 2)
        separators = (',', ': ')
        sort_keys = True
        obj = from_rdf(self.store, context_data, base,
                       auto_compact=auto_compact)
        data = json.dumps(obj, indent=indent, separators=separators,
                          sort_keys=sort_keys)

        stream.write(data.encode(encoding, 'replace'))


def from_rdf(graph, context_data=None, base=None,
        use_native_types=False, auto_compact=False, startnode=None, index=False):
    # TODO: docstring w. args and return value
    # TODO: support for use_native_types, index and startnode

    if not context_data and auto_compact:
        context_data = dict(
            (pfx, unicode(ns))
            for (pfx, ns) in graph.namespaces() if pfx and
            unicode(ns) != u"http://www.w3.org/XML/1998/namespace")

    if isinstance(context_data, Context):
        context = context_data
        context_data = context.to_dict()
    else:
        context = Context(context_data, base=base)

    # TODO: bug in rdflib? plain triples end up in separate unnamed graphs
    if graph.context_aware:
        default_graph = Graph()
        graphs = [default_graph]
        for g in graph.contexts():
            if isinstance(g.identifier, URIRef):
                graphs.append(g)
            else:
                default_graph += g
    else:
        graphs = [graph]

    use_compact = bool(context)

    objs = []
    for g in graphs:
        obj = {}
        graphname = None

        if isinstance(g.identifier, URIRef):
            graphname = context.shrink_iri(g.identifier)
            obj[context.id_key] = graphname

        nodes = _from_graph(g, context)

        if not graphname and len(nodes) == 1:
            obj.update(nodes[0])
        else:
            if not nodes:
                continue
            obj[context.graph_key] = nodes

        if objs and objs[0].get(context.get_key(ID)) == graphname:
            objs[0].update(obj)
        else:
            objs.append(obj)

    if len(graphs) == 1 and len(objs) == 1 and not context_data:
        default = objs[0]
        items = default.get(context.graph_key)
        if len(default) == 1 and items:
            objs = items
    elif len(objs) == 1 and use_compact:
        objs = objs[0]

    if context_data:
        if isinstance(objs, list):
            objs = {context.get_key(GRAPH): objs}
        objs[CONTEXT] = context_data

    return objs


def _from_graph(graph, context):
    nodemap = {}

    for s in set(graph.subjects()):
        ## only iri:s and unreferenced (rest will be promoted to top if needed)
        if isinstance(s, URIRef) or (isinstance(s, BNode)
                and not any(graph.subjects(None, s))):
            _process_subject(graph, context, s, nodemap)

    return nodemap.values()


def _process_subject(graph, context, s, nodemap):
    node, node_id = {}, None
    if isinstance(s, URIRef):
        node_id = context.shrink_iri(s)
    elif any(graph.subjects(None, s)) and isinstance(s, BNode):
        node_id = s.n3()
    if node_id in nodemap:
        return None
    node[context.id_key] = node_id
    nodemap[node_id] = node
    p_objs = {}
    for p, o in graph.predicate_objects(s):
        objs = p_objs.setdefault(p, [])
        objs.append(o)
    for p, objs in p_objs.items():
        p_key, onode = _get_key_and_result(graph, context, s, p, objs, nodemap)
        node[p_key] = onode

    return node


def _get_key_and_result(graph, context, s, p, objs, nodemap):

    repr_value = lambda o: _to_raw_value(graph, context, s, o, nodemap)
    iri_to_id = (lambda o:
                 context.shrink_iri(o) if isinstance(o, URIRef) else o)
    iri_to_symbol = (lambda o:
                 context.to_symbol(o) if isinstance(o, URIRef) else o)

    datatype = None
    if isinstance(objs[0], Literal):
        datatype = unicode(objs[0].datatype)
        for other in objs[1:]:
            if not isinstance(other, Literal) or other.datatype != datatype:
                datatype = None
                break

    term = context.find_term(unicode(p), datatype)
    if term:
        p_key = term.name
        if term.container == SET:
            many = True
        else:
            many = not len(objs) == 1
        if term.type:
            if term.type == ID:
                repr_value = iri_to_id
            if term.type == VOCAB:
                repr_value = iri_to_symbol
            else:
                repr_value = (lambda o:
                    o if unicode(o.datatype) == term.type
                    else _to_raw_value(graph, context, s, o, nodemap))
    else:
        p_key = context.to_symbol(p)
        if not term and p == RDF.type:
            repr_value = iri_to_symbol
            p_key = context.type_key
        many = not context or len(objs) != 1

    # TODO: working, but in need of refactoring...
    if term and term.container == LIST:
        wrapped_repr = repr_value
        repr_value = lambda o: wrapped_repr(o)[context.list_key]

    nodes = [repr_value(o) for o in objs]
    if not many:
        nodes = nodes[0]

    return p_key, nodes


def _to_raw_value(graph, context, s, o, nodemap):
    coll = _to_collection(graph, context, s, o, nodemap)
    if coll is not None:
        return {context.list_key: coll}
    elif isinstance(o, BNode):
        embed = False # TODO: auto_compact or using startnode and only one ref
        onode = _process_subject(graph, context, o, nodemap)
        if onode:
            if embed and not any(s2 for s2 in graph.subjects(None, o) if s2 != s):
                return onode
            else:
                nodemap[onode[context.id_key]] = onode
        return {context.id_key: o.n3()}
    elif isinstance(o, URIRef):
        # TODO: embed if o != startnode (else reverse)
        return {context.id_key: context.shrink_iri(o)}
    elif isinstance(o, Literal):
        v = o
        if o.datatype:
            #https://github.com/RDFLib/rdflib-jsonld/issues/4
            #serialize data type regardless
            #if context and o.datatype in PLAIN_LITERAL_TYPES:
            #    return o.toPython()
            return {context.type_key: context.to_symbol(o.datatype),
                    context.value_key: v}
        elif o.language and o.language != context.language:
            return {context.lang_key: o.language,
                    context.value_key: v}
        elif not context or context.language and not o.language:
            return {context.value_key: v}
        else:
            return v


def _to_collection(graph, context, s, l, nodemap):
    if l != RDF.nil and not graph.value(l, RDF.first):
        return None
    list_nodes = []
    chain = set([l])
    while l:
        if l == RDF.nil:
            return list_nodes
        if isinstance(l, URIRef):
            return None
        first, rest = None, None
        for p, o in graph.predicate_objects(l):
            if not first and p == RDF.first:
                first = o
            elif not rest and p == RDF.rest:
                rest = o
            elif p != RDF.type or o != RDF.List:
                return None
        lnode = _to_raw_value(graph, context, s, first, nodemap)
        list_nodes.append(lnode)
        l = rest
        if l in chain:
            return None
        chain.add(l)

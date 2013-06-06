# -*- coding: utf-8 -*-
from rdflib.py3compat import format_doctest_out as uformat
uformat("""
This parser will read in an JSON-LD formatted document and create an RDF
Graph. See:

    http://json-ld.org/

Example usage::

    >>> from rdflib import Graph, URIRef, Literal
    >>> test_json = '''
    ... {
    ...     "@context": {
    ...         "dc": "http://purl.org/dc/terms/",
    ...         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    ...         "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
    ...     },
    ...     "@id": "http://example.org/about",
    ...     "dc:title": {
    ...         "@language": "en",
    ...         "@literal": "Someone's Homepage"
    ...     }
    ... }
    ... '''
    >>> g = Graph().parse(data=test_json, format='json-ld')
    >>> list(g) == [(URIRef('http://example.org/about'),
    ...     URIRef('http://purl.org/dc/terms/title'),
    ...     Literal(%(u)s"Someone's Homepage", lang=%(u)s'en'))]
    True

"""
        )
# NOTE: This code reads the entire JSON object into memory before parsing, but
# we should consider streaming the input to deal with arbitrarily large graphs.

import warnings
from rdflib.parser import Parser
from rdflib.namespace import RDF, XSD
from rdflib.term import URIRef, BNode, Literal

from ldcontext import Context, Term, \
        CONTEXT_KEY, ID_KEY, REV_KEY, LIST_KEY, INDEX_KEY, LANG_KEY
from ldcontext import source_to_json

__all__ = ['JsonLDParser', 'to_rdf']


class JsonLDParser(Parser):
    def __init__(self):
        super(JsonLDParser, self).__init__()

    def parse(self, source, sink, **kwargs):
        """
        @@ TODO: add docstring describing args and returned value type
        """
        encoding = kwargs.get('encoding') or 'utf-8'
        if encoding not in ('utf-8', 'utf-16'):
            warnings.warn("JSON should be encoded as unicode. " +
                          "Given encoding was: %s" % encoding)

        base = kwargs.get('base') or sink.absolutize(
            source.getPublicId() or source.getSystemId() or "")

        context_data = kwargs.get('context')

        tree = source_to_json(source)
        to_rdf(tree, sink, base, context_data)


def to_rdf(data, graph, base=None, context_data=None):
    """
    @@ TODO: add docstring describing args and returned value type
    """
    context = Context()

    if isinstance(data, list):
        resources = data
    elif isinstance(data, dict):
        resources = data.get(context.graph_key, data)
        if not isinstance(resources, list):
            resources = [resources]
        context_data = data.get(CONTEXT_KEY) or context_data

    if context_data:
        context.load(context_data)

    if context.vocab:
        graph.bind(None, context.vocab)
    for term in context.terms:
        if term.iri and term.iri.endswith(('/', '#', ':')):
            graph.bind(term.key, term.iri)

    state = graph, context, base
    for node in resources:
        _add_to_graph(state, node)

    return graph

import re
bNodeIdRegexp = re.compile(r'^_:(.+)')


def _add_to_graph(state, node):
    graph, context, base = state
    if not isinstance(node, dict) or context.value_key in node:
        return

    l_ctx = node.get(CONTEXT_KEY)
    if l_ctx:
        context = Context(context.to_dict())
        context.load(l_ctx)

    id_val = node.get(context.id_key)
    if isinstance(id_val, unicode) and (not bNodeIdRegexp.match(id_val)):
        subj = URIRef(context.expand(id_val), base)
    else:
        subj = BNode()

    for pred_key, obj in node.items():
        term = None

        if not isinstance(obj, list):
            obj_nodes = [obj]
        else:
            obj_nodes = obj

        if pred_key in (CONTEXT_KEY, context.id_key):
            continue
        if pred_key == context.type_key:
            pred = RDF.type
            term = Term(None, None, context.id_key)
        elif pred_key == context.graph_key:
            for onode in obj_nodes:
                _add_to_graph(state, onode)
            continue
        else:
            pred_uri = context.expand(pred_key)
            if not pred_uri:
                continue
            pred = URIRef(pred_uri)
            # TODO: refactor context to get_term by key or iri
            term = context._term_map.get(pred_key) or context.get_term(pred_uri)

        if term:
            if term.container == LIST_KEY:
                obj_nodes = [{context.list_key: obj_nodes}]
            elif isinstance(obj, dict):
                if term.container == INDEX_KEY:
                    obj_nodes = []
                    for values in obj.values():
                        if not isinstance(values, list):
                            obj_nodes.append(values)
                        else:
                            obj_nodes += values
                elif term.container == LANG_KEY:
                    obj_nodes = []
                    for lang, values in obj.items():
                        if not isinstance(values, list):
                            values = [values]
                        for v in values:
                            obj_nodes.append((v, lang))

        for obj_node in obj_nodes:
            obj = _to_object(state, term, obj_node)
            if obj is None:
                continue
            if term and term.coercion == REV_KEY:
                graph.add((obj, pred, subj))
            else:
                graph.add((subj, pred, obj))

    return subj


def _to_object(state, term, node):
    graph, context, base = state

    if node is None:
        return

    if isinstance(node, tuple):
        value, lang = node
        if value is None:
            return
        return Literal(value, lang=lang)

    if isinstance(node, dict) and context.list_key in node:
        node_list = node.get(context.list_key)
        if node_list:
            first_subj = BNode()
            l_subj, l_next = first_subj, None
            for l_node in node_list:
                if l_next:
                    graph.add((l_subj, RDF.rest, l_next))
                    l_subj = l_next
                l_obj = _to_object(state, None, l_node)
                if l_obj is None:
                    continue
                graph.add((l_subj, RDF.first, l_obj))
                l_next = BNode()
            graph.add((l_subj, RDF.rest, RDF.nil))
            return first_subj
        else:
            node = {context.id_key: unicode(RDF.nil)}

    if not isinstance(node, dict):
        if not term or not term.coercion:
            if isinstance(node, float):
                # TODO: JSON-LD promotes double over decimal;
                # verify correctness...
                return Literal(node, datatype=XSD.double)
            return Literal(node, lang=context.lang)
        else:
            if term.coercion == ID_KEY:
                node = {context.id_key: context.expand(node)}
            else:
                node = {context.type_key: term.coercion,
                        context.value_key: node}

    if context.value_key in node:
        value = node[context.value_key]
        if value is None:
            return
        if context.lang_key in node:
            return Literal(value, lang=node[context.lang_key])
        elif context.type_key and context.type_key in node:
            return Literal(value,
                        datatype=context.expand(node[context.type_key]))
        else:
            return Literal(value)
    else:
        return _add_to_graph(state, node)

# -*- coding: utf-8 -*-
from rdflib.py3compat import format_doctest_out as uformat
uformat("""
This parser will interpret a JSON-LD document as an RDF Graph. See:

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
from rdflib.graph import ConjunctiveGraph
from rdflib.parser import Parser
from rdflib.namespace import RDF, XSD
from rdflib.term import URIRef, BNode, Literal

from .context import Context, Term, UNDEF
from .util import source_to_json, VOCAB_DELIMS
from .keys import CONTEXT, GRAPH, ID, INDEX, LANG, LIST, REV, SET, TYPE, VALUE, VOCAB

__all__ = ['JsonLDParser', 'to_rdf']


TYPE_TERM = Term(unicode(RDF.type), TYPE, VOCAB)


class JsonLDParser(Parser):
    def __init__(self):
        super(JsonLDParser, self).__init__()

    def parse(self, source, sink, **kwargs):
        # TODO: docstring w. args and return value
        encoding = kwargs.get('encoding') or 'utf-8'
        if encoding not in ('utf-8', 'utf-16'):
            warnings.warn("JSON should be encoded as unicode. " +
                          "Given encoding was: %s" % encoding)
        base = kwargs.get('base') or sink.absolutize(
            source.getPublicId() or source.getSystemId() or "")
        context_data = kwargs.get('context')
        data = source_to_json(source)
        conj_sink = ConjunctiveGraph(
            store=sink.store, identifier=sink.identifier)
        to_rdf(data, conj_sink, base, context_data)


def to_rdf(data, graph, base=None, context_data=None):
    # TODO: docstring w. args and return value
    context = Context(base=base)

    if context_data:
        context.load(context_data)

    if isinstance(data, list):
        resources = data
    elif isinstance(data, dict):
        l_ctx = data.get(CONTEXT)
        if l_ctx:
            context.load(l_ctx)
        resources = data
        if not isinstance(resources, list):
            resources = [resources]

    if context.vocab:
        graph.bind(None, context.vocab)
    for name, term in context.terms.items():
        if term.id and term.id.endswith(VOCAB_DELIMS):
            graph.bind(name, term.id)

    for node in resources:
        _add_to_graph(graph, context, node)

    return graph


def _add_to_graph(graph, context, node, rootgraph=None):
    if not isinstance(node, dict) or context.get_value(node):
        return

    if rootgraph is None:
        rootgraph = graph

    if CONTEXT in node:
        l_ctx = node.get(CONTEXT)
        if l_ctx:
            context = context.subcontext(l_ctx)
        else:
            context = Context(base=context.doc_base)

    id_val = context.get_id(node)
    if isinstance(id_val, unicode):
        subj = _to_rdf_id(context, id_val)
    else:
        subj = BNode()

    for key, obj in node.items():
        if key in (CONTEXT, ID, context.get_key(ID)):
            continue
        if key in (REV, context.get_key(REV)):
            for rkey, robj in obj.items():
                _key_to_graph(graph, context, subj, rkey, robj, rootgraph, True)
        else:
            _key_to_graph(graph, context, subj, key, obj, rootgraph)

    return subj


def _key_to_graph(graph, context, subj, key, obj, rootgraph, reverse=False):

    if isinstance(obj, list):
        obj_nodes = obj
    else:
        obj_nodes = [obj]

    term = context.terms.get(key)
    if term:
        term_id = term.id
        if term.container == LIST:
            obj_nodes = [{LIST: obj_nodes}]
        elif isinstance(obj, dict):
            if term.container == INDEX:
                obj_nodes = []
                for values in obj.values():
                    if not isinstance(values, list):
                        obj_nodes.append(values)
                    else:
                        obj_nodes += values
            elif term.container == LANG:
                obj_nodes = []
                for lang, values in obj.items():
                    if not isinstance(values, list):
                        values = [values]
                    for v in values:
                        obj_nodes.append((v, lang))
    else:
        term_id = None

    if TYPE in (key, term_id):
        term = TYPE_TERM
    elif GRAPH in (key, term_id):
        if graph is rootgraph:
            #assert graph.context_aware
            subgraph = rootgraph.get_context(subj)
        else:
            subgraph = graph
        for onode in obj_nodes:
            _add_to_graph(subgraph, context, onode, rootgraph)
        return
    elif SET in (key, term_id):
        for onode in obj_nodes:
            _add_to_graph(graph, context, onode, rootgraph)
        return

    pred_uri = term.id if term else context.expand(key)

    flattened = []
    for obj in obj_nodes:
        if isinstance(obj, dict):
            objs = context.get_set(obj)
            if objs is not None:
                obj = objs
        if isinstance(obj, list):
            flattened += obj
            continue
        flattened.append(obj)
    obj_nodes = flattened

    if not pred_uri:
        return

    if term and term.reverse:
        reverse = not reverse

    pred = URIRef(pred_uri)
    for obj_node in obj_nodes:
        obj = _to_object(graph, context, term, obj_node)
        if obj is None:
            continue
        if reverse:
            graph.add((obj, pred, subj))
        else:
            graph.add((subj, pred, obj))


def _to_object(graph, context, term, node, inlist=False):

    if node is None:
        return

    if isinstance(node, tuple):
        value, lang = node
        if value is None:
            return
        return Literal(value, lang=lang)

    if isinstance(node, dict):
        node_list = context.get_list(node)
        if node_list is not None:
            if inlist: # TODO: and NO_LISTS_OF_LISTS
                return
            listref = _add_list(graph, context, term, node_list)
            if listref:
                return listref

    else: # expand..
        if not term or not term.type:
            if isinstance(node, float):
                return Literal(node, datatype=XSD.double)
            if term and term.language is not UNDEF:
                lang = term.language
            else:
                lang = context.language
            return Literal(node, lang=lang)
        else:
            if term.type == ID:
                node = {ID: context.resolve(node)}
            elif term.type == VOCAB:
                node = {ID: context.expand(node) or context.resolve_iri(node)}
            else:
                node = {TYPE: term.type,
                        VALUE: node}

    lang = context.get_language(node)
    if lang or context.get_key(VALUE) in node or VALUE in node:
        value = context.get_value(node)
        if value is None:
            return None
        datatype = not lang and context.get_type(node) or None
        if lang:
            return Literal(value, lang=lang)
        elif datatype:
            return Literal(value, datatype=context.expand(datatype))
        else:
            return Literal(value)
    else:
        return _add_to_graph(graph, context, node)


def _to_rdf_id(context, id_val):
    bid = _get_bnodeid(id_val)
    if bid:
        return BNode(bid)
    else:
        return URIRef(context.resolve(id_val))


def _get_bnodeid(ref):
    if not ref.startswith('_:'):
        return
    bid = ref.split('_:', 1)[-1]
    return bid or None


def _add_list(graph, context, term, node_list):
    if not isinstance(node_list, list):
        node_list = [node_list]
    first_subj = BNode()
    subj, rest = first_subj, None
    for node in node_list:
        if node is None:
            continue
        if rest:
            graph.add((subj, RDF.rest, rest))
            subj = rest
        obj = _to_object(graph, context, term, node, inlist=True)
        if obj is None:
            continue
        graph.add((subj, RDF.first, obj))
        rest = BNode()
    if rest:
        graph.add((subj, RDF.rest, RDF.nil))
        return first_subj
    else:
        return RDF.nil

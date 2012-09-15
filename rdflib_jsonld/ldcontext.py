# -*- coding: utf-8 -*-
"""
Implementation of a Linked Data Context structure based on the JSON-LD
definition of contexts. See:

    http://json-ld.org/

"""

# from __future__ import with_statement
from urlparse import urljoin
try:
    import json
except ImportError:
    import simplejson as json

from rdflib.namespace import RDF, split_uri
from rdflib.parser import create_input_source


RDF_TYPE = unicode(RDF.type)

CONTEXT_KEY = '@context'
LANG_KEY = '@language'
ID_KEY = '@id'
TYPE_KEY = '@type'
VALUE_KEY = '@value'
LIST_KEY = '@list'
CONTAINER_KEY = '@container'
SET_KEY = '@set'
REV_KEY = '@rev'  # EXPERIMENTAL
GRAPH_KEY = '@graph'
VOCAB_KEY = '@vocab'
KEYS = set(
    [LANG_KEY, ID_KEY, TYPE_KEY, VALUE_KEY, LIST_KEY, REV_KEY, GRAPH_KEY])


class Context(object):

    def __init__(self, source=None):
        self._key_map = {}
        self._iri_map = {}
        self._term_map = {}
        self.lang = None
        self.vocab = None
        if source:
            self.load(source)

    terms = property(lambda self: self._term_map.values())

    context_key = CONTEXT_KEY
    lang_key = property(lambda self: self._key_map.get(LANG_KEY, LANG_KEY))
    id_key = property(lambda self: self._key_map.get(ID_KEY, ID_KEY))
    type_key = property(lambda self: self._key_map.get(TYPE_KEY, TYPE_KEY))
    value_key = property(lambda self: self._key_map.get(VALUE_KEY, VALUE_KEY))
    list_key = property(lambda self: self._key_map.get(LIST_KEY, LIST_KEY))
    container_key = CONTAINER_KEY
    set_key = SET_KEY
    rev_key = property(lambda self: self._key_map.get(REV_KEY, REV_KEY))
    graph_key = property(lambda self: self._key_map.get(GRAPH_KEY, GRAPH_KEY))
    vocab_key = VOCAB_KEY

    def load(self, source, base=None, visited_urls=None):
        if CONTEXT_KEY in source:
            source = source[CONTEXT_KEY]
        if isinstance(source, list):
            sources = source
        else:
            sources = [source]
        for data in sources:
            if isinstance(data, basestring):
                url = urljoin(base, data)
                visited_urls = visited_urls or []
                visited_urls.append(url)
                sub_defs = source_to_json(url)
                self.load(sub_defs, base, visited_urls)
                continue
            for key, value in data.items():
                if key == LANG_KEY:
                    self.lang = value
                elif key == self.vocab_key:
                    self.vocab = value
                elif isinstance(value, unicode) and value in KEYS:
                    self._key_map[value] = key
                else:
                    term = self._create_term(data, key, value)
                    self.add_term(term)

    def _create_term(self, data, key, dfn):
        if isinstance(dfn, dict):
            iri = self._rec_expand(data, dfn.get(ID_KEY))
            coercion = self._rec_expand(data, dfn.get(TYPE_KEY))
            container = dfn.get(CONTAINER_KEY)
            if not container and dfn.get(LIST_KEY) is True:
                container = LIST_KEY
            return Term(iri, key, coercion, container)
        else:
            iri = self._rec_expand(data, dfn)
            return Term(iri, key)

    def _rec_expand(self, data, expr, prev=None):
        if expr == prev:
            return expr
        pfx, nxt = self._prep_expand(expr)
        if pfx:
            nxt = data.get(pfx) + nxt
        return self._rec_expand(data, nxt, expr)

    def _prep_expand(self, expr):
        if ':' in expr:
            pfx, local = expr.split(':', 1)
            if not local.startswith('//'):
                return pfx, local
        return None, expr

    def add_term(self, term):
        self._iri_map[term.iri] = term
        self._term_map[term.key] = term

    def get_term(self, iri):
        return self._iri_map.get(iri)

    def shrink(self, iri):
        iri = unicode(iri)
        term = self._iri_map.get(iri)
        if term:
            return term.key
        if iri == RDF_TYPE:
            # NOTE: only if no term for the rdf:type IRI is defined
            return self.type_key
        try:
            ns, name = split_uri(iri)
            term = self._iri_map.get(ns)
            if term:
                return ":".join((term.key, name))
            elif ns == self.vocab:
                return name
        except:
            pass
        return iri

    def expand(self, term_curie_or_iri):
        term_curie_or_iri = unicode(term_curie_or_iri)
        pfx, local = self._prep_expand(term_curie_or_iri)
        # TODO: is empty string pfx (test/tests/rdf-0009.jsonld) really ok?
        #if pfx:
        if pfx is not None:
            ns = self._term_map.get(pfx)
            if ns and ns.iri:
                return ns.iri + local
        else:
            term = self._term_map.get(term_curie_or_iri)
            if term:
                return term.iri
            elif self.vocab:
                return self.vocab + term_curie_or_iri
        return term_curie_or_iri

    def to_dict(self):
        data = {}
        if self.lang:
            data[LANG_KEY] = self.lang
        if self.vocab:
            data[VOCAB_KEY] = self.vocab
        for key, alias in self._key_map.items():
            if key != alias:
                data[alias] = key
        for term in self.terms:
            obj = term.iri
            if term.coercion:
                obj = {IRI_KEY: term.iri}
                if term.coercion == REV_KEY:
                    obj = {REV_KEY: term.iri}
                else:
                    obj[TYPE_KEY] = term.coercion
            if term.container:
                obj[CONTAINER_KEY] = term.container
            if obj:
                data[term.key] = obj
        return data


class Term(object):
    def __init__(self, iri, key, coercion=None, container=None):
        self.iri = iri
        self.key = key
        self.coercion = coercion
        self.container = container


def source_to_json(source):
    # TODO: conneg for JSON (fix support in rdflib's URLInputSource!)
    source = create_input_source(source)

    stream = source.getByteStream()
    try:
        return json.load(stream)
    finally:
        stream.close()



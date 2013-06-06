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
    assert json  # workaround for pyflakes issue #13
except ImportError:
    import simplejson as json

from rdflib.namespace import RDF, split_uri
from rdflib.parser import create_input_source
from rdflib.py3compat import PY3
if PY3:
    from io import StringIO

RDF_TYPE = unicode(RDF.type)

CONTEXT_KEY = '@context'
LANG_KEY = '@language'
ID_KEY = '@id'
TYPE_KEY = '@type'
VALUE_KEY = '@value'
LIST_KEY = '@list'
CONTAINER_KEY = '@container'
SET_KEY = '@set'
INDEX_KEY = '@index'
REV_KEY = '@reverse'
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
        self._loaded = False
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

    def __nonzero__(self):
        return self._loaded

    def load(self, source, base=None, visited_urls=None):
        self._loaded = True
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
                self.load(sub_defs, url, visited_urls)
                continue
            self.lang = data.get(LANG_KEY, self.lang)
            self.vocab = data.get(VOCAB_KEY, self.vocab)
            for key, value in data.items():
                if key in (LANG_KEY, VOCAB_KEY, '_'):
                    continue
                elif isinstance(value, unicode) and value in KEYS:
                    self._key_map[value] = key
                else:
                    term = self._create_term(data, key, value)
                    self.add_term(term)

    def _create_term(self, data, key, dfn):
        if isinstance(dfn, dict):
            coercion = None
            if REV_KEY in dfn:
                iri = self._rec_expand(data, dfn.get(REV_KEY))
                coercion = REV_KEY
            elif ID_KEY not in dfn and self.vocab:
                iri = self.vocab + key
            else:
                iri = self._rec_expand(data, dfn.get(ID_KEY))
            if not coercion:
                type_val = dfn.get(TYPE_KEY)
                if type_val in (ID_KEY, TYPE_KEY):
                    coercion = type_val
                else:
                    coercion = self._rec_expand(data, type_val)
            return Term(iri, key, coercion, dfn.get(CONTAINER_KEY))
        else:
            iri = self._rec_expand(data, dfn)
            return Term(iri, key)

    def _rec_expand(self, data, expr, prev=None):
        if expr == prev:
            return expr
        is_term, pfx, nxt = self._prep_expand(expr)
        if is_term and self.vocab:
            return self.vocab + expr
        if pfx:
            iri = data.get(pfx) or self.expand(pfx)
            nxt = iri + nxt
        return self._rec_expand(data, nxt, expr)

    def _prep_expand(self, expr):
        if ':' not in expr:
            return True, None, expr
        pfx, local = expr.split(':', 1)
        if not local.startswith('//'):
            return False, pfx, local
        else:
            return False, None, expr

    def add_term(self, term):
        self._iri_map.setdefault(term.iri, []).append(term)
        self._term_map[term.key] = term

    def get_term(self, iri):
        # TODO: pick based on datatype/is_ref/is_list
        candidates = self._iri_map.get(iri)
        if candidates:
            return candidates[0]
        else:
            return None

    def shrink(self, iri):
        iri = unicode(iri)
        term = self.get_term(iri)
        if term:
            return term.key
        if iri == RDF_TYPE:
            # NOTE: only if no term for the rdf:type IRI is defined
            return self.type_key
        try:
            ns, name = split_uri(iri)
            term = self.get_term(iri)
            if term:
                return ":".join((term.key, name))
            elif ns == self.vocab:
                return name
        except:
            pass
        return iri

    def expand(self, term_curie_or_iri):
        term_curie_or_iri = unicode(term_curie_or_iri)
        is_term, pfx, local = self._prep_expand(term_curie_or_iri)
        if pfx is not None:
            ns = self._term_map.get(pfx)
            if ns and ns.iri:
                return ns.iri + local
        else:
            term = self._term_map.get(term_curie_or_iri)
            if term:
                return term.iri
            elif self.vocab and ':' not in term_curie_or_iri:
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
            if term.coercion or term.container:
                obj = {ID_KEY: term.iri}
            if term.coercion:
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
        if PY3:
            return json.load(StringIO(stream.read().decode('utf-8')))
        else:
            return json.load(stream)
    finally:
        stream.close()

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
LITERAL_KEY = '@value'
LIST_KEY = '@list'
CONTAINER_KEY = '@container' # EXPERIMENTAL
SET_KEY = '@set' # EXPERIMENTAL
REV_KEY = '@rev' # EXPERIMENTAL

KEYS = set([LANG_KEY, ID_KEY, TYPE_KEY, LITERAL_KEY, LIST_KEY, REV_KEY])


class Context(object):

    def __init__(self, source=None):
        self._key_map = {}
        self._iri_map = {}
        self._term_map = {}
        self.lang = None
        if source:
            self.load(source)

    terms = property(lambda self: self._term_map.values())

    context_key = CONTEXT_KEY
    lang_key = property(lambda self: self._key_map.get(LANG_KEY, LANG_KEY))
    id_key = property(lambda self: self._key_map.get(ID_KEY, ID_KEY))
    type_key = property(lambda self: self._key_map.get(TYPE_KEY, TYPE_KEY))
    literal_key = property(lambda self: self._key_map.get(LITERAL_KEY, LITERAL_KEY))
    list_key = property(lambda self: self._key_map.get(LIST_KEY, LIST_KEY))
    container_key = CONTAINER_KEY
    set_key = SET_KEY
    rev_key = property(lambda self: self._key_map.get(REV_KEY, REV_KEY))

    def load(self, source, base=None, visited_urls=None):
        if CONTEXT_KEY in source:
            source = source[CONTEXT_KEY]
        if isinstance(source, list): 
            sources = source 
        else:
            sources=[source]
        terms, simple_terms = [], []
        for obj in sources:
            if isinstance(obj, basestring):
                url = urljoin(base, obj)
                visited_urls = visited_urls or []
                visited_urls.append(url)
                sub_defs = source_to_json(url)
                self.load(sub_defs, base, visited_urls)
                continue
            for key, value in obj.items():
                if key == LANG_KEY:
                    self.lang = value
                elif isinstance(value, unicode) and value in KEYS:
                    self._key_map[value] = key
                else:
                    term = self._create_term(key, value)
                    if term.coercion:
                        terms.append(term)
                    else:
                        simple_terms.append(term)
        for term in simple_terms + terms:
            # TODO: expansion for these shoold be done by recursively looking up
            # keys in source (would also avoid this use of simple_terms).
            if term.iri:
                term.iri = self.expand(term.iri)
            if term.coercion:
                term.coercion = self.expand(term.coercion)
            self.add_term(term)

    def _create_term(self, key, dfn):
        if isinstance(dfn, dict):
            iri = dfn.get(ID_KEY)
            coercion = dfn.get(TYPE_KEY)
            container = dfn.get(CONTAINER_KEY)
            if not container and dfn.get(LIST_KEY) is True:
                container = LIST_KEY
            return Term(iri, key, coercion, container)
        else:
            iri = self.expand(dfn)
            return Term(iri, key)

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
        except:
            pass
        return iri

    def expand(self, term_curie_or_iri):
        term_curie_or_iri = unicode(term_curie_or_iri)
        if ':' in term_curie_or_iri:
            pfx, term = term_curie_or_iri.split(':', 1)
            ns = self._term_map.get(pfx)
            if ns and ns.iri:
                return ns.iri + term
        else:
            term = self._term_map.get(term_curie_or_iri)
            if term:
                return term.iri
        return term_curie_or_iri

    def to_dict(self):
        data = {}
        if self.lang:
            data[LANG_KEY] = self.lang
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
                if term.container == LIST_KEY:
                    obj[LIST_KEY] = True # TODO: deprecated form?
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
    
    stream=source.getByteStream()
    try: 
        return json.load(stream)
    finally: 
        stream.close()



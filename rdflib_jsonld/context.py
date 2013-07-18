# -*- coding: utf-8 -*-
"""
Implementation of the JSON-LD Context structure. See:

    http://json-ld.org/

"""
from urlparse import urljoin
from rdflib.namespace import RDF, split_uri

from . import util
from .keys import (BASE, CONTAINER, CONTEXT, GRAPH, ID, INDEX, LANG, LIST,
        REV, SET, TYPE, VALUE, VOCAB)


NODE_KEYS = set([LANG, ID, TYPE, VALUE, LIST, SET, REV, GRAPH])

class Defined(int): pass
UNDEF = Defined(0)


class Context(object):

    def __init__(self, source=None, base=None):
        self.language = None
        self.vocab = None
        self.base = base
        self.doc_base = base
        self.alias = {}
        self.terms = {}
        self._lookup = {}
        self._prefixes = {}
        self._loaded = False
        if source:
            self.load(source)

    def __nonzero__(self):
        return self._loaded

    def load(self, source, base=None):
        self._loaded = True
        sources = not isinstance(source, list) and [source] or source
        for source in sources:
            if isinstance(source, basestring):
                url = urljoin(base, source)
                #if url in visited_urls: continue
                #visited_urls.append(url)
                source = util.source_to_json(url)
            if CONTEXT in source:
                source = source[CONTEXT]
            self._read_source(source)

    def subcontext(self, source):
        # IMPROVE: to optimize, implement SubContext with parent fallback support
        ctx = Context()
        ctx.language = self.language
        ctx.vocab = self.vocab
        ctx.base = self.base
        ctx.doc_base = self.doc_base
        ctx.alias = self.alias.copy()
        ctx.terms = self.terms.copy()
        ctx._lookup = self._lookup.copy()
        ctx._prefixes = self._prefixes.copy()
        ctx.load(source)
        return ctx

    def get_id(self, obj):
        return self._get(obj, ID)

    def get_type(self, obj):
        return self._get(obj, TYPE)

    def get_language(self, obj):
        return self._get(obj, LANG)

    def get_value(self, obj):
        return self._get(obj, VALUE)

    def get_graph(self, obj):
        return self._get(obj, GRAPH)

    def get_list(self, obj):
        return self._get(obj, LIST)

    def get_set(self, obj):
        return self._get(obj, SET)

    def get_rev(self, obj):
        return self._get(obj, REV)

    def _get(self, obj, key):
        return obj.get(self.alias.get(key)) or obj.get(key)

    def get_key(self, key):
        return self.alias.get(key, key)

    lang_key = property(lambda self: self.get_key(LANG))
    id_key = property(lambda self: self.get_key(ID))
    type_key = property(lambda self: self.get_key(TYPE))
    value_key = property(lambda self: self.get_key(VALUE))
    list_key = property(lambda self: self.get_key(LIST))
    rev_key = property(lambda self: self.get_key(REV))
    graph_key = property(lambda self: self.get_key(GRAPH))

    def add_term(self, name, idref, coercion=UNDEF, container=UNDEF,
            language=UNDEF, reverse=False):
        term = Term(idref, name, coercion, container, language, reverse)
        self.terms[name] = term
        self._lookup[(idref, coercion or language, container, reverse)] = term
        self._prefixes[idref] = name

    def find_term(self, idref, coercion=None, container=None,
            language=None, reverse=False):
        lu = self._lookup
        coercion = coercion or language
        if coercion and container:
            found = lu.get((idref, coercion, container, reverse))
            if found: return found
        if coercion:
            found = lu.get((idref, coercion, UNDEF, reverse))
            if found: return found
        if container:
            found = lu.get((idref, UNDEF, container, reverse))
            if found: return found
        return lu.get((idref, UNDEF, UNDEF, reverse))

    def resolve(self, curie_or_iri):
        iri = self.expand(curie_or_iri, False)
        return self.resolve_iri(iri)

    def resolve_iri(self, iri):
        if self.base:
            return urljoin(self.base, iri).replace('../', '')
        else:
            return iri

    def expand(self, term_curie_or_iri, use_vocab=True):
        is_term, pfx, local = self._prep_expand(term_curie_or_iri)
        if pfx is not None:
            ns = self.terms.get(pfx)
            if ns and ns.id:
                return ns.id + local
        elif is_term and use_vocab:
            if self.vocab:
                return self.vocab + term_curie_or_iri
            else:
                term = self.terms.get(term_curie_or_iri)
                if term:
                    return term.id
            return None
        return self.resolve_iri(term_curie_or_iri)

    def shrink(self, iri):
        ns, name = split_uri(unicode(iri))
        pfx = self._prefixes.get(ns)
        if pfx:
            return u":".join((pfx, name))
        elif ns == self.vocab:
            return name
        return iri

    def _read_source(self, source):
        for key, value in source.items():
            if key  == '_':
                continue
            if key == LANG:
                self.language = value
            elif key == VOCAB:
                self.vocab = value
            elif key == BASE:
                if value is None:
                    self.base = self.doc_base
                else:
                    self.base = value
            elif isinstance(value, basestring) and value in NODE_KEYS:
                self.alias[value] = key
            else:
                self._read_term(source, key, value)

    def _read_term(self, source, name, dfn):
        if isinstance(dfn, dict):
            #term = self._create_term(source, key, value)
            rev = dfn.get(REV)
            idref = rev or dfn.get(ID, UNDEF)
            if idref == TYPE:
                idref = unicode(RDF.type)
            elif idref is not UNDEF:
                idref = self._rec_expand(source, idref)
            elif ':' in name:
                idref = self._rec_expand(source, name)
            elif self.vocab:
                idref = self.vocab + name
            coercion = dfn.get(TYPE, UNDEF)
            if coercion and coercion not in (ID, TYPE, VOCAB):
                coercion = self._rec_expand(source, coercion)
            self.add_term(name, idref, coercion,
                    dfn.get(CONTAINER, UNDEF), dfn.get(LANG, UNDEF), bool(rev))
        else:
            idref = self._rec_expand(source, dfn)
            self.add_term(name, idref)

    def _rec_expand(self, source, expr, prev=None):
        if expr == prev:
            return expr
        is_term, pfx, nxt = self._prep_expand(expr)
        #nxt = source.get(nxt) or prev_source.get(nxt) or nxt
        if is_term and self.vocab:
            return self.vocab + expr
        if pfx:
            iri = source.get(pfx) or self.expand(pfx)
            if isinstance(iri, dict):
                iri = iri.get(ID)
            nxt = iri + nxt
        return self._rec_expand(source, nxt, expr)

    def _prep_expand(self, expr):
        if ':' not in expr:
            return True, None, expr
        pfx, local = expr.split(':', 1)
        if not local.startswith('//'):
            return False, pfx, local
        else:
            return False, None, expr


class Term(object):
    def __init__(self, idref, name, coercion=UNDEF, container=UNDEF,
            language=UNDEF, reverse=False):
        self.name = name
        self.id = idref
        self.type = coercion
        self.container = container
        self.language = language
        self.reverse = reverse

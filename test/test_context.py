"""
JSON-LD Context Spec
"""
from __future__ import unicode_literals
from rdflib_jsonld.context import Context, Term
from rdflib_jsonld import errors


def test_create_context():
    ctx = Context()
    ctx.add_term('label', 'http://example.org/ns/label')
    term = ctx.terms.get('label')

    assert term.name == 'label'
    assert ctx.find_term('http://example.org/ns/label') is term


def test_select_term_based_on_value_characteristics():
    ctx = Context()

    ctx.add_term('updated', 'http://example.org/ns/updated')
    ctx.add_term('updatedDate', 'http://example.org/ns/updated',
        coercion='http://www.w3.org/2001/XMLSchema#date')

    assert ctx.find_term('http://example.org/ns/updated').name == 'updated'
    assert ctx.find_term('http://example.org/ns/updated',
        coercion='http://www.w3.org/2001/XMLSchema#date').name == 'updatedDate'

    #ctx.find_term('http://example.org/ns/title_sv', language='sv')

    #ctx.find_term('http://example.org/ns/authorList', container='@set')

    #ctx.find_term('http://example.org/ns/creator', reverse=True)


def test_getting_keyword_values_from_nodes():
    ctx = Context()
    assert ctx.get_id({'@id': 'urn:x:1'}) == 'urn:x:1'
    assert ctx.get_language({'@language': 'en'}) == 'en'


def parsing_a_context_expands_prefixes():
    ctx = Context({
        '@vocab': 'http://example.org/ns/',
        'x': 'http://example.org/ns/',
        'label': 'x:label',
        'x:updated': {'@type': 'x:date'}})

    term = ctx.terms.get('label')

    assert term.id == 'http://example.org/ns/label'

    term = ctx.terms.get('x:updated')
    assert term.id == 'http://example.org/ns/updated'
    assert term.type == 'http://example.org/ns/date'


def expanding_terms():
    ctx = Context()
    assert ctx.expand('term') == 'http://example.org/ns/term'
    assert ctx.expand('x:term') == 'http://example.org/ns/term'


def shrinking_iris():
    ctx = Context()
    assert ctx.shrink_iri('http://example.org/ns/term') == 'x:term'
    assert ctx.to_symbol('http://example.org/ns/term') == 'term'


def resolving_iris():
    ctx = Context({'@base': 'http://example.org/path/leaf'})
    assert ctx.resolve('/') == 'http://example.org/'
    assert ctx.resolve('/trail') == 'http://example.org/trail'
    assert ctx.resolve('../') == 'http://example.org/'
    assert ctx.resolve('../../') == 'http://example.org/'


def accessing_keyword_values_by_alias():
    ctx = Context({'iri': '@id', 'lang': '@language'})
    assert ctx.get_id({'iri': 'urn:x:1'}) == 'urn:x:1'
    assert ctx.get_language({'lang': 'en'}) == 'en'


def standard_keywords_still_work():
    ctx = Context()
    assert ctx.get_id({'@id': 'urn:x:1'}) == 'urn:x:1'


def representing_keywords_by_alias():
    ctx = Context()
    assert ctx.id_key == 'iri'
    assert ctx.lang_key == 'lang'


def creating_a_subcontext():
    ctx4 = ctx.subcontext({'lang': '@language'})
    assert ctx4.get_language({'lang': 'en'}) == 'en'

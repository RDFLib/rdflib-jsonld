# JSON-LD Context Spec
from rdflib_jsonld.context import Context, Term


def test_create_context():
    ctx = Context()
    ctx.add_term(u'label', u'http://example.org/ns/label')
    term = ctx.terms.get(u'label')

    assert term.name == u'label'
    assert ctx.find_term(u'http://example.org/ns/label') is term


def test_select_term_based_on_value_characteristics():
    ctx = Context()

    ctx.add_term(u'updated', u'http://example.org/ns/updated')
    ctx.add_term(u'updatedDate', u'http://example.org/ns/updated',
        coercion=u'http://www.w3.org/2001/XMLSchema#date')

    assert ctx.find_term(u'http://example.org/ns/updated').name == u'updated'
    assert ctx.find_term(u'http://example.org/ns/updated',
        coercion=u'http://www.w3.org/2001/XMLSchema#date').name == u'updatedDate'

    #ctx.find_term(u'http://example.org/ns/title_sv', language=u'sv')

    #ctx.find_term(u'http://example.org/ns/authorList', container=u'@set')

    #ctx.find_term(u'http://example.org/ns/creator', reverse=True)


def test_getting_keyword_values_from_nodes():
    ctx = Context()
    assert ctx.get_id({u'@id': u'urn:x:1'}) == u'urn:x:1'
    assert ctx.get_language({u'@language': u'en'}) == u'en'


def parsing_a_context_expands_prefixes():
    ctx = Context({
        u'@vocab': u'http://example.org/ns/',
        u'x': u'http://example.org/ns/',
        u'label': u'x:label',
        u'x:updated': {u'@type': u'x:date'}})

    term = ctx.terms.get(u'label')

    assert term.id == u'http://example.org/ns/label'

    term = ctx.terms.get(u'x:updated')
    assert term.id == u'http://example.org/ns/updated'
    assert term.type == u'http://example.org/ns/date'


def expanding_terms():
    ctx = Context()
    assert ctx.expand(u'term') == u'http://example.org/ns/term'
    assert ctx.expand(u'x:term') == u'http://example.org/ns/term'


def shrinking_iris():
    ctx = Context()
    assert ctx.shrink_iri(u'http://example.org/ns/term') == u'x:term'
    assert ctx.to_symbol(u'http://example.org/ns/term') == u'term'


def resolving_iris():
    ctx = Context({u'@base': u'http://example.org/path/leaf'})
    assert ctx.resolve(u'/') == u'http://example.org/'
    assert ctx.resolve(u'/trail') == u'http://example.org/trail'
    assert ctx.resolve(u'../') == u'http://example.org/'
    assert ctx.resolve(u'../../') == u'http://example.org/'


def accessing_keyword_values_by_alias():
    ctx = Context({u'iri': u'@id', u'lang': u'@language'})
    assert ctx.get_id({u'iri': u'urn:x:1'}) == u'urn:x:1'
    assert ctx.get_language({u'lang': u'en'}) == u'en'


def standard_keywords_still_work():
    ctx = Context()
    assert ctx.get_id({u'@id': u'urn:x:1'}) == u'urn:x:1'


def representing_keywords_by_alias():
    ctx = Context()
    assert ctx.id_key == u'iri'
    assert ctx.lang_key == u'lang'


def creating_a_subcontext():
    ctx4 = ctx.subcontext({u'lang': u'@language'})
    assert ctx4.get_language({u'lang': u'en'}) == u'en'


Context Spec:

    >>> from rdflib_jsonld.context import Context, Term

    >>> ctx = Context()

    >>> ctx.add_term(u'label', u'http://example.org/ns/label')
    >>> term = ctx.terms.get(u'label')
    >>> term.name
    u'label'

    >>> ctx.find_term(u'http://example.org/ns/label') is term
    True

Selecting term based on value characteristics:

    >>> ctx.add_term(u'updated', u'http://example.org/ns/updated')
    >>> ctx.add_term(u'updatedDate', u'http://example.org/ns/updated',
    ...     coercion=u'http://www.w3.org/2001/XMLSchema#date')

    >>> ctx.find_term(u'http://example.org/ns/updated').name
    u'updated'
    >>> ctx.find_term(u'http://example.org/ns/updated',
    ...     coercion=u'http://www.w3.org/2001/XMLSchema#date').name
    u'updatedDate'

    >>> ctx.find_term(u'http://example.org/ns/title_sv', language=u'sv')
    >>>

    >>> ctx.find_term(u'http://example.org/ns/authorList', container=u'@set')
    >>>

    >>> ctx.find_term(u'http://example.org/ns/creator', reverse=True)
    >>>

Getting keyword values from nodes:

    >>> ctx.get_id({u'@id': u'urn:x:1'})
    u'urn:x:1'
    >>> ctx.get_language({u'@language': u'en'})
    u'en'

Parsing a context expands prefixes:

    >>> ctx = Context({
    ...     u'@vocab': u'http://example.org/ns/',
    ...     u'x': u'http://example.org/ns/',
    ...     u'label': u'x:label',
    ...     u'x:updated': {u'@type': u'x:date'}})
    >>> term = ctx.terms.get(u'label')

    >>> term.id
    u'http://example.org/ns/label'

    >>> term = ctx.terms.get(u'x:updated')
    >>> term.id
    u'http://example.org/ns/updated'
    >>> term.type
    u'http://example.org/ns/date'

Expanding terms:

    >>> ctx.expand(u'term')
    u'http://example.org/ns/term'

    >>> ctx.expand(u'x:term')
    u'http://example.org/ns/term'

Shrinking IRIs:

    >>> ctx.shrink_iri(u'http://example.org/ns/term')
    u'x:term'

    >>> ctx.to_symbol(u'http://example.org/ns/term')
    u'term'

Resolving IRIs:

    >>> ctx = Context({u'@base': u'http://example.org/path/leaf'})
    >>> ctx.resolve(u'/')
    u'http://example.org/'
    >>> ctx.resolve(u'/trail')
    u'http://example.org/trail'
    >>> ctx.resolve(u'../')
    u'http://example.org/'
    >>> ctx.resolve(u'../../')
    u'http://example.org/'

Accessing keyword values by alias:

    >>> ctx = Context({u'iri': u'@id', u'lang': u'@language'})
    >>> ctx.get_id({u'iri': u'urn:x:1'})
    u'urn:x:1'
    >>> ctx.get_language({u'lang': u'en'})
    u'en'

Standard keywords still work:

    >>> ctx.get_id({u'@id': u'urn:x:1'})
    u'urn:x:1'

Representing keywords by alias:

    >>> ctx.id_key
    u'iri'

    >>> ctx.lang_key
    u'lang'

Creating a subcontext:

    >>> ctx4 = ctx.subcontext({u'lang': u'@language'}) #doctest: +ELLIPSIS
    >>> ctx4.get_language({u'lang': u'en'})
    u'en'


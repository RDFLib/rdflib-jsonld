.. _rdflib_jsonld.jsonld_serializer: an RDFLib plugin JSONLD serializer

=======================================
JSONLD serializer plug-in for RDFLib
=======================================

Using the plug-in JSONLD serializer with RDFLib
------------------------------------------------

The plugin serializer is automatically registered if installed by
setuptools.

Read in an RDFLib Graph and serialize it, specifying ``format='json-ld'``.

.. code-block:: python

    >>> from rdflib import Graph, plugin

    >>> testrdf = """
    ... @prefix dcterms: <http://purl.org/dc/terms/> .
    ... <http://example.org/about>
    ...     dcterms:title "Someone's Homepage"@en .
    ... """

    >>> g = Graph().parse(data=testrdf, format='n3')

    >>> print(g.serialize(format='json-ld', indent=4))
    {
        "@context": {
            "dcterms": "http://purl.org/dc/terms/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
        },
        "@id": "http://example.org/about",
        "dcterms:title": {
            "@language": "en",
            "@value": "Someone's Homepage"
        }
    }

Module contents
---------------

.. currentmodule:: rdflib_jsonld.serializer

.. autoclass:: JsonLDSerializer
   :members: serialize

.. autofunction:: from_rdf

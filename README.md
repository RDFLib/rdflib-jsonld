RDFLib plugin providing JSON-LD parsing and serialization.
==========================================================

This parser/serialiser will ---

* read in an JSON-LD formatted document and create an RDF graph 
* serialize an RDF graph to JSON-LD formatted output 


Using the plug-in JSONLD serializer/parser with RDFLib
-------------------------------------------------------

The plugin parser and serializer are automatically registered if installed by
setuptools, otherwise call ``rdfextras.registerplugins()`` after importing,
as shown below:

    >>> from rdflib import Graph, plugin
    >>> from rdflib.serializer import Serializer
    >>> import rdfextras
    >>> rdfextras.registerplugins() # if no setuptools

    >>> testrdf = '''
    ... @prefix dc: <http://purl.org/dc/terms/> .
    ... <http://example.org/about>
    ...     dc:title "Someone's Homepage"@en .
    ... '''

    >>> g = Graph().parse(data=testrdf, format='n3')

    >>> g.serialize(format='json-ld', indent=4)
    {
        "@id": "http://example.org/about",
        "http://purl.org/dc/terms/title": {
            "@language": "en",
            "@value": "Someone's Homepage"
        }
    }
    >>> g.serialize(format='json-ld', indent=4, compact=True)
    {
        "@context": {
            "dc": "http://purl.org/dc/terms/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@id": "http://example.org/about",
        "dc:title": {
            "@language": "en",
            "@value": "Someone's Homepage"
        }
    }


Building the Sphinx documentation
---------------------------------

If Sphinx is installed, Sphinx documentation can be generated with::

    $ python setup.py build_sphinx

The documentation will be created in ./build/sphinx.

Continuous integration tests
----------------------------

[![Build Status](https://travis-ci.org/RDFLib/rdflib-jsonld.png?branch=master)](https://travis-ci.org/RDFLib/rdflib-jsonld)

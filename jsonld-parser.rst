.. _rdfextras.parsers.rdfjson: an rdfxtras plugin parser

===================================
JSONLD parser plugin for rdflib
===================================
|today|

JSONLD
------

Read a JSON-LD formatted document into RDF. Described on the `JSON-LD <http://json-ld.org/>`_ web site as:

    JSON-LD (JavaScript Object Notation for Linking Data) is a lightweight Linked Data format that gives your data context. It is easy for humans to read and write. It is easy for machines to parse and generate. It is based on the already successful JSON format and provides a way to help JSON data interoperate at Web-scale. If you are already familiar with JSON, writing JSON-LD is very easy. These properties make JSON-LD an ideal Linked Data interchange language for JavaScript environments, Web service, and unstructured databases such as CouchDB and MongoDB.

    A simple example of a JSON object expressing Linked Data:
    
    .. code-block:: js
        
        { 
          "@context": "http://json-ld.org/contexts/person",
          "@id": "http://dbpedia.org/resource/John_Lennon",
          "name": "John Lennon",
          "birthday": "10-09",
          "member": "http://dbpedia.org/resource/The_Beatles"
        }
    
    The example above describes a person whose name is John Lennon. The difference between regular JSON and JSON-LD is that the JSON-LD object above uniquely identifies itself on the Web and can be used, without introducing ambiguity, across every Web site, Web service and JSON-based database in operation today. The secret lies in the @context, which instructs Linked Data-aware processors on how to interpret the JSON object.


Using the plug-in JSONLD parser with rdflib
---------------------------------------------

Usage with rdflib is straightforward: if required register the plugin, identify a source 
of JSON-LD, pass the source to the parser, manipulate the resulting graph.

.. code-block:: python

    >>> from rdflib import Graph, URIRef, Literal
    >>> from rdflib.parser import Parser
    >>> import rdfextras
    >>> rdfextras.registerplugins() # if no setuptools
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


Modules
-------

.. currentmodule:: rdfextras.parsers.jsonld

.. automodule:: rdfextras.parsers.jsonld

.. autoclass:: JsonLDParser
   :members: parse

.. autofunction:: rdfextras.parsers.jsonld.to_rdf

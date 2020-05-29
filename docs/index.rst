.. rdflib_jsonld documentation master file

Welcome to rdflib_jsonld's documentation!
=========================================

RDFLib plugin providing JSON-LD parsing and serialization.

This parser/serialiser will 

* read in an JSON-LD formatted document and create an RDF graph 
* serialize an RDF graph to JSON-LD formatted output 

JSON-LD is described on the `JSON-LD <http://json-ld.org/>`_ web site as:

    JSON-LD (JavaScript Object Notation for Linking Data) is a lightweight
    Linked Data format that gives your data context. It is easy for humans
    to read and write. It is easy for machines to parse and generate. It is
    based on the already successful JSON format and provides a way to help
    JSON data interoperate at Web-scale. If you are already familiar with
    JSON, writing JSON-LD is very easy. These properties make JSON-LD an
    ideal Linked Data interchange language for JavaScript environments, Web
    service, and unstructured databases such as CouchDB and MongoDB.

    A simple example of a JSON object expressing Linked Data:
    
    .. code-block:: js
        
        { 
          "@context": "http://json-ld.org/contexts/person",
          "@id": "http://dbpedia.org/resource/John_Lennon",
          "name": "John Lennon",
          "birthday": "10-09",
          "member": "http://dbpedia.org/resource/The_Beatles"
        }
    
    The example above describes a person whose name is John Lennon. The
    difference between regular JSON and JSON-LD is that the JSON-LD object
    above uniquely identifies itself on the Web and can be used, without
    introducing ambiguity, across every Web site, Web service and
    JSON-based database in operation today. The secret lies in the ``@context``
    which instructs Linked Data-aware processors on how to interpret
    the JSON object.


Contents:

.. toctree::
   :maxdepth: 2

   jsonld-serializer
   jsonld-parser


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


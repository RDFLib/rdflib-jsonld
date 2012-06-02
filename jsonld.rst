.. _rdfextras.serializers.rdfjson: an rdfxtras plugin serializer

=======================================
JSONLD serializer plug-in for rdflib
=======================================
|today|

Using the plug-in JSONLD serializer with rdflib
------------------------------------------------

Usage with rdflib is straightforward: register the plugin, load in an rdflib 
Graph, serialize the graph.

.. warning:: Under construction

.. code-block:: python

    >>> from rdflib import Graph, plugin
    >>> from rdflib.serializer import Serializer
    >>> import rdfextras
    >>> rdfextras.registerplugins()

    >>> testrdf = '''
    ... @prefix dc: <http://purl.org/dc/terms/> .
    ... <http://example.org/about>
    ...     dc:title "Someone's Homepage"@en .
    ... '''

    >>> g = Graph().parse(data=testrdf, format='n3')

    >>> print(g.serialize(format='json-ld', indent=4))
    {
        "@context": {
            "dc": "http://purl.org/dc/terms/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
        },
        "@id": "http://example.org/about",
        "dc:title": {
            "@language": "en",
            "@literal": "Someone's Homepage"
        }
    }


Modules
--------

.. currentmodule:: rdfextras.serializers.jsonld

.. automodule:: rdfextras.serializers.jsonld

.. autoclass:: JsonLDSerializer
   :members: serialize

.. autofunction:: to_tree



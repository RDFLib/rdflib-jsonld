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


Building the Sphinx documentation
---------------------------------

If Sphinx is installed, Sphinx documentation can be generated with::

    $ python setup.py build_sphinx

The documentation will be created in ./build/sphinx.


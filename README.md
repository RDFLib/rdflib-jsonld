# RDFLib plugin providing JSON-LD parsing and serialization

This is an implementation of [JSON-LD](http://www.w3.org/TR/json-ld/)
for [RDFLib](https://github.com/RDFLib/rdflib).
For more information about this technology, see the [JSON-LD website](http://json-ld.org/).

This implementation will:

- read in an JSON-LD formatted document and create an RDF graph
- serialize an RDF graph to JSON-LD formatted output


## Installation

The easiest way to install the RDFLib JSON-LD plugin is directly from PyPi using pip by running the command below:

```shell
pip install rdflib-jsonld
```

Otherwise you can download the source and install it directly by running:

```shell
python setup.py install
```


## Using the plug-in JSONLD serializer/parser with RDFLib

The plugin parser and serializer are automatically registered if installed by
setuptools.

```python
>>> from rdflib import Graph, plugin
>>> from rdflib.serializer import Serializer

>>> testrdf = '''
... @prefix dc: <http://purl.org/dc/terms/> .
... <http://example.org/about>
...     dc:title "Someone's Homepage"@en .
... '''

>>> g = Graph().parse(data=testrdf, format='n3')

>>> print(g.serialize(format='json-ld', indent=4))
{
    "@id": "http://example.org/about",
    "http://purl.org/dc/terms/title": [
        {
            "@language": "en",
            "@value": "Someone's Homepage"
        }
    ]
}

>>> context = {"@vocab": "http://purl.org/dc/terms/", "@language": "en"}
>>> print(g.serialize(format='json-ld', context=context, indent=4))
{
    "@context": {
        "@language": "en",
        "@vocab": "http://purl.org/dc/terms/"
    },
    "@id": "http://example.org/about",
    "title": "Someone's Homepage"
}
```

<!-- CUT HERE -->
<!-- Text after this comment won't appear on PyPI -->

## Building the Sphinx documentation

If Sphinx is installed, Sphinx documentation can be generated with:

```shell
$ python setup.py build_sphinx
```

The documentation will be created in ./build/sphinx.


## Continuous integration tests

[![Build Status](https://travis-ci.org/RDFLib/rdflib-jsonld.svg?branch=master)](https://travis-ci.org/RDFLib/rdflib-jsonld)

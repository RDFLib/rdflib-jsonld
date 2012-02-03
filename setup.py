from setuptools import setup

# Requires simplejson if Python version < 2.6

setup(
    name = 'rdflib-jsonld',
    version = '0.1',
    description = "rdflib extension adding JSON-LD parser and serializer",
    author = "Graham Higgins",
    author_email = "gjhiggins@gmail.com",
    url = "http://github.com/RDFLib/rdflib-jsonld",
    packages = ["rdflib_jsonld"],
    test_suite = "test",
    install_requires = ["rdflib>=3.0", "rdfextras>=0.1"],
    entry_points = {
        'rdf.plugins.parser': [
            'json-ld = rdflib_jsonld.jsonld_parser:JsonLDParser',
        ],
        'rdf.plugins.serializer': [
            'json-ld = rdflib_jsonld.jsonld_serializer:JsonLDSerializer',
        ],
    }

)

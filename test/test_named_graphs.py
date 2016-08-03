from __future__ import unicode_literals, print_function
from rdflib import *
from rdflib.plugin import register, Parser
register('application/ld+json', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')

data = """
{
    "@context": {"@vocab": "http://schema.org/"},
    "@graph": [
        { "@id": "http://example.org/data#jdoe",
          "name": "John"
        },
        { "@id": "http://example.org/data#janedoe",
          "name": "Jane"
        },
        { "@id": "http://example.org/data#metadata",
          "@graph": [
              { "@id": "http://example.org/data",
                "creator": "http://example.org/data#janedoe"
              }
          ]
        }
    ]
}
"""

meta_ctx = URIRef('http://example.org/data#metadata')

def test_graph():
    g = Graph()
    g.parse(data=data, format="application/ld+json")
    assert len(g) == 2

def test_conjunctive_graph():
    cg = ConjunctiveGraph()
    cg.parse(data=data, format="application/ld+json")
    assert len(cg) == 3

    print("default graph (%s) contains %s triples (expected 2)" % (cg.identifier, len(cg.default_context)))
    contexts = {ctx.identifier: ctx for ctx in cg.contexts()}
    for ctx in contexts.values():
        print("named graph (%s) contains %s triples" % (ctx.identifier, len(ctx)))
    # TODO: see <https://github.com/RDFLib/rdflib/issues/436>
    #assert len(cg.default_context) == 2
    #assert len(contexts) == 2

def test_dataset():
    ds = Dataset()
    ds.parse(data=data, format="application/ld+json", publicID=ds.default_context.identifier)
    assert len(ds) == 3

    assert len(ds.default_context) == 2
    print("default graph (%s) contains %s triples (expected 2)" % (ds.identifier, len(ds.default_context)))
    contexts = {ctx.identifier: ctx for ctx in ds.contexts()}
    assert len(contexts) == 2
    assert len(contexts.pop(meta_ctx)) == 1
    assert len(contexts.values()[0]) == 2

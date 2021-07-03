from __future__ import unicode_literals, print_function
from rdflib import *
from rdflib.plugin import register, Parser

register("application/ld+json", Parser, "rdflib_jsonld.parser", "JsonLDParser")

data = """
{
    "@context": {
        "@version": 1.1,
        "@vocab": "http://example.org/",
        "name": "label",
        "note": "comment",
        "Person": {
          "@context": {
            "name": "name"
          }
        },
        "Book": {
          "@context": {
            "name": "title"
          }
        },
        "chapter": {
          "@context": {
            "name": "title"
          }
        },
        "common": "@nest",
        "details": "@nest"
    },
    "@graph": [
        {
          "@type": "Thing",
          "name": "Some Thing"
        },
        {
          "@type": "Person",
          "name": "Some Body"
        },
        {
          "@type": "Book",
          "name": "Somewhere",
          "author": {
            "name": "Someone"
          }
        },
        {
          "chapter": {
            "name": "Beginning"
          }
        },
        {
          "common": {
            "name": "Common"
          },
          "details": {
            "note": "Detailed"
          }
        }
    ]
}
"""


def test_graph():
    g = Graph()
    g.parse(data=data, format="application/ld+json")
    ttl = g.serialize(format="text/turtle").decode("utf8")
    print(ttl)
    assert """ :label "Some Thing" """ in ttl
    assert """ :name "Some Body" """ in ttl
    assert """ :title "Somewhere" """ in ttl
    assert """ :label "Someone" """ in ttl
    assert """ :title "Beginning" """ in ttl
    assert "nest" not in ttl
    assert """ :label "Common" """ in ttl
    assert """ :comment "Detailed" """

from __future__ import unicode_literals, print_function
from rdflib import *
from rdflib.plugin import register, Parser
register('application/ld+json', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')

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
          "name": "Somewhere"
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
    ttl = g.serialize(format='text/turtle').decode('utf8')
    print(ttl)
    assert \
            ''' :label "Some Thing" ''' in ttl and \
            ''' :name "Some Body" ''' in ttl and \
            ''' :title "Somewhere" ''' in ttl and \
            ''' :title "Beginning" ''' in ttl and \
            'nest' not in ttl and \
            ''' :label "Common" ''' in ttl and \
            ''' :comment "Detailed" ''' in ttl
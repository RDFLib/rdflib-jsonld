# -*- coding: utf-8 -*-
import unittest
import json
from rdflib import ConjunctiveGraph, Graph
from rdflib.compare import isomorphic
from rdflib_jsonld.jsonld_parser import to_rdf
# from rdflib_jsonld.jsonld_serializer import to_tree


test01_in = """\
{
  "@context": {"foaf": "http://xmlns.com/foaf/0.1/"},
  "@id": "http://greggkellogg.net/foaf#me",
  "foaf:name": "Gregg Kellogg"
}"""

test01_in = """\
{
  "@id": "http://greggkellogg.net/foaf#me",
  "http://xmlns.com/foaf/0.1/name": "Gregg Kellogg"
}
"""

test01_out = """\
<http://greggkellogg.net/foaf#me> \
<http://xmlns.com/foaf/0.1/name> \
"Gregg Kellogg" \
.
"""

test02_in = """\
{
  "@context": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "@language": "ja"
  },
  "foaf:name": "花澄",
  "foaf:occupation": "科学者"
}"""

test03_in = """\
{
  "@context": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "@language": "ja"
  },
  "foaf:name": "花澄",
  "foaf:occupation": {
    "@value": "Scientist",
    "@language": "en"
  }
}"""



class CoreTest(unittest.TestCase):

    def test01(self):
        # tree, graph, base=None, context_data=None
        g = ConjunctiveGraph()
        ingraph = to_rdf(json.loads(test01_in), g)
        outgraph = ConjunctiveGraph()
        outgraph.parse(data=test01_out, format="nquads")
        assert isomorphic(outgraph, ingraph), \
                "Expected graph of %s:\n%s\nGot graph of %s:\n %s" % (
                        len(outgraph), outgraph.serialize(),
                        len(ingraph), ingraph.serialize())

    def test02(self):
        ingraph = to_rdf(json.loads(test02_in), ConjunctiveGraph())
        outgraph = ConjunctiveGraph().parse(
            data=ingraph.serialize(format="xml"), format="xml")
        assert isomorphic(outgraph, ingraph), \
                "Expected graph of %s:\n%s\nGot graph of %s:\n %s" % (
                        len(outgraph), outgraph.serialize(),
                        len(ingraph), ingraph.serialize())

    def test03(self):
        ingraph = to_rdf(json.loads(test03_in), ConjunctiveGraph())
        outgraph = ConjunctiveGraph().parse(
            data=ingraph.serialize(format="xml"), format="xml")
        assert isomorphic(outgraph, ingraph), \
                "Expected graph of %s:\n%s\nGot graph of %s:\n %s" % (
                        len(outgraph), outgraph.serialize(),
                        len(ingraph), ingraph.serialize())

if __name__ == "__main__":
    unittest.main()

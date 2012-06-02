import unittest
# from nose.exc import SkipTest
from rdflib import Graph

test03_n3 = """\
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

<http://example.org/people#joebob> a foaf:Person;
  foaf:name "Joe Bob";
  foaf:nick ( "joe" "bob" "jaybee" ) .
"""

test03_json = """\
{
  "@context":
  {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  },
  "@id": "http://example.org/people#joebob",
  "@type": "foaf:Person",
  "foaf:name": "Joe Bob",
  "foaf:nick":
  {
    "@list": [ "joe", "bob", "jaybee" ]
  }
}
"""

test02_n3 = """\
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

<http://manu.sporny.org/i/public>
  a foaf:Person;
  foaf:name "Manu Sporny";
  foaf:knows [ a foaf:Person; foaf:name "Gregg Kellogg" ] .
"""

test02_json = """\
{
  "@context":
  {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  },
  "@id": "http://manu.sporny.org/i/public",
  "@type": "foaf:Person",
  "foaf:name": "Manu Sporny",
  "foaf:knows":
  {
    "@type": "foaf:Person",
    "foaf:name": "Gregg Kellogg"
  }
}
"""

test01_n3 = """\
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

<http://manu.sporny.org/i/public> a foaf:Person;
  foaf:name "Manu Sporny";
  foaf:homepage <http://manu.sporny.org/> .
"""
test01_json = """\
{
  "@context":
  {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  },
  "@id": "http://manu.sporny.org/i/public",
  "@type": "foaf:Person",
  "foaf:name": "Manu Sporny",
  "foaf:homepage": { "@id": "http://manu.sporny.org/" }
}
"""


class JsonLDParserTestCase(unittest.TestCase):
    identifier = "rdflib_test"

    def setUp(self):
        self.json_graph = Graph()
        self.n3_graph = Graph()

    def tearDown(self):
        self.json_graph = self.n3_graph = None

    def test_parse01(self):
        g = self.json_graph.parse(data=test01_json, format="json-ld")
        self.n3_graph.parse(data=test01_n3, format="n3")
        self.assertTrue(self.json_graph.isomorphic(self.n3_graph))

    def test_parse02(self):
        self.json_graph.parse(data=test02_json, format="json-ld")
        self.n3_graph.parse(data=test02_n3, format="n3")
        self.assertTrue(self.json_graph.isomorphic(self.n3_graph))

    def test_parse03(self):
        self.json_graph.parse(data=test03_json, format="json-ld")
        self.n3_graph.parse(data=test03_n3, format="n3")
        self.assertTrue(self.json_graph.isomorphic(self.n3_graph))


# Slightly lame, assumes JSON-LD parsing is error-free
class JsonLDSerializerTestCase(unittest.TestCase):
    identifier = "rdflib_test"

    def setUp(self):
        self.n3_graph = Graph()

    def tearDown(self):
        self.n3_graph = None

    def test_serialize_01(self):
        self.n3_graph.parse(data=test01_n3, format="n3")
        json_data = self.n3_graph.serialize(data=test01_json, format="json-ld")
        gjson = Graph()
        self.assert_(gjson.parse(data=json_data, format="json-ld"
                      ).isomorphic(self.n3_graph))

    def test_serialize_02(self):
        self.n3_graph.parse(data=test02_n3, format="n3")
        json_data = self.n3_graph.serialize(data=test02_json, format="json-ld")
        gjson = Graph()
        self.assert_(gjson.parse(data=json_data, format="json-ld"
                    ).isomorphic(self.n3_graph))

    def test_serialize_03(self):
        self.n3_graph.parse(data=test03_n3, format="n3")
        json_data = self.n3_graph.serialize(data=test03_json, format="json-ld")
        gjson = Graph()
        self.assert_(gjson.parse(data=json_data, format="json-ld"
                    ).isomorphic(self.n3_graph))

from rdflib.plugin import register, Parser
register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')
from rdflib import Graph, URIRef, Literal
test_json = '''
{
  "@context": "https://json-ld.org/contexts/person.jsonld",
  "@id": "http://dbpedia.org/resource/John_Lennon",
  "name": "John Lennon",
  "born": "1940-10-09",
  "spouse": "http://dbpedia.org/resource/Cynthia_Lennon"
}
'''
g = Graph().parse(data=test_json, format='json-ld')
list(g) == [(URIRef('http://example.org/about'),URIRef('http://purl.org/dc/terms/title'),Literal("Someone's Homepage", lang='en'))]
print(list(g))
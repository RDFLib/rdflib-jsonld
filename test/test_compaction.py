from rdflib import Graph, plugin
from rdflib.serializer import Serializer


cases = []
def case(*args): cases.append(args)


case("""@prefix dc: <http://purl.org/dc/terms/> .
<http://example.org/>
    dc:title "Homepage"@en .
""",
{"@vocab": "http://purl.org/dc/terms/", "@language": "en"},
"""
{
    "@context": "/context.jsonld",
    "@id": "http://example.org/",
    "title": "Homepage"
}
""")


case("""@prefix dc: <http://purl.org/dc/terms/> .
<http://example.org/>
    dc:title "Homepage"@en, "Hemsida"@sv .
""",
{"@vocab": "http://purl.org/dc/terms/", "title": {"@container": "@language"}},
"""
{
    "@context": "/context.jsonld",
    "@id": "http://example.org/",
    "title": {
        "en": "Homepage",
        "sv": "Hemsida"
    }
}
""")


case("""@prefix dc: <http://purl.org/dc/terms/> .
<http://example.org/>
    dc:title "Homepage"@en, "Hemsida"@sv .
""",
{"@vocab": "http://purl.org/dc/terms/", "@language": "sv", "title_en": {"@id": "title", "@language": "en"}},
"""
{
    "@context": "/context.jsonld",
    "@id": "http://example.org/",
    "title_en": "Homepage",
    "title": "Hemsida"
}
""")


case("""
@prefix : <http://example.org/ns#> .
<http://example.org/> :has _:b1 .
""",
{"has": {"@type": "@id", "@id": "http://example.org/ns#has"}},
"""
{
    "@context": "/context.jsonld",
    "@id": "http://example.org",
    "has": "_:b1"
}
""")


case("""
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://example.org/ns#> .
:Something rdfs:subClassOf :Thing .
""",
{
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "v": "http://example.org/ns#",
    "subClassOf": {"@id": "rdfs:subClassOf", "@type": "@id", "@container": "@set"}
},
"""
{
    "@context": "/context.jsonld",
    "@id": "v:Something",
    "subClassOf": ["v:Thing"]
}
""")


case("""
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <http://example.org/ns#> .
:World owl:unionOf (:Everyhing :Nothing) .
""",
{
    "owl": "http://www.w3.org/2002/07/owl#",
    "v": "http://example.org/ns#",
    "unionOf": {"@id": "owl:unionOf", "@type": "@id", "@container": "@list"}
},
"""
{
    "@context": "/context.jsonld",
    "@id": "v:World",
    "unionOf": ["v:Everyhing", "v:Nothing"]
}
""")


#    dc:title "Homepage"@en, "Home Page"@en, "Hemsida"@sv .

#    dc:title "Homepage"@en, "Home Page"@en-GB, "Hemsida"@sv .


#def test_cases():
#        yield run, data, context, output
if __name__ == '__main__':
    for data, context, output in cases:
        g = Graph().parse(data=data, format='n3')
        print(g.serialize(format='json-ld', context=context, indent=4))

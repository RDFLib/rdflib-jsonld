from rdflib import Graph
from rdflib.plugin import register, Parser, Serializer

register("json-ld", Parser, "rdflib_jsonld.parser", "JsonLDParser")
register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")


def test_issue_61():
    context_jsonld = "61-context.jsonld"
    data_file = "61-data.jsonld"

    g = Graph().parse(data_file, format="json-ld")
    output = g.serialize(format="json-ld", context=context_jsonld, indent=4)

    assert "dct:spatial" in output
    assert '"spatial"' not in output

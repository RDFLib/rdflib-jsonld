from rdflib import *
from rdflib.plugin import register, Parser
from rdflib.namespace import RDF, RDFS
# monkey-patch N-Quads parser via it's underlying W3CNTriplesParser to keep source bnode id:s ..
from rdflib.plugins.parsers.ntriples import W3CNTriplesParser, r_nodeid, bNode


def _preserving_nodeid(self, bnode_context=None):
    if not self.peek("_"):
        return False
    return bNode(self.eat(r_nodeid).group(1))


W3CNTriplesParser.nodeid = _preserving_nodeid


JLD = Namespace("https://w3c.github.io/json-ld-api/tests/vocab#")
MF = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")

# register("application/ld+json", Parser, "rdflib_jsonld.parser", "JsonLDParser")
register("json-ld", Parser, "rdflib_jsonld.parser", "JsonLDParser")


g = Graph().parse("1.1/toRdf-manifest.jsonld", format="json-ld")


g_context = Graph(base="https://w3c.github.io/json-ld-api/tests/toRdf/").parse("1.1/context.jsonld", format="json-ld")
# g_context_testing = """{
#   "@context": {
#     "@base": "https://w3c.github.io/json-ld-api/tests/toRdf/"
#   }
# }"""
# g_context.parse(data=g_context_testing, format="json-ld")
for s in g.subjects(predicate=RDF.type, object=JLD.ToRDFTest):
    id = str(s).split("#")[-1]
    name = None
    input = None
    expect = None
    for p, o in g.predicate_objects(subject=s):
        if p == MF.name:
            name = str(o)
        elif p == MF.action:
            input = str(o)
        elif p == MF.result:
            expect = str(o)
        elif p == RDFS.comment:
            purpose = str(o)
    print(f"{id} {input} {expect}")
    g_in = Graph(base="https://w3c.github.io/json-ld-api/tests/toRdf/").parse(input, format="json-ld")
    g_out = Graph().parse(expect, format="nquads")
    if not g_in.isomorphic(g_out):
        g_in = Graph().parse("https://w3c.github.io/json-ld-api/tests/toRdf/0016-in.jsonld", format="json-ld")
        print(purpose)
        print(g_in.serialize())
        print(g_out.serialize())

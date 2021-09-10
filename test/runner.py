from __future__ import with_statement
import json
import rdflib
from rdflib import ConjunctiveGraph
from rdflib.compare import isomorphic
from rdflib_jsonld._compat import IS_PY3
from rdflib_jsonld.parser import to_rdf
from rdflib_jsonld.serializer import from_rdf
from rdflib_jsonld.keys import CONTEXT, GRAPH


# monkey-patch NTriplesParser to keep source bnode id:s ..
from rdflib.plugins.parsers.ntriples import r_nodeid, bNode

# NTriplesParser was renamed between 5.0.0 and 6.0.0.
if rdflib.__version__ < "6":
    from rdflib.plugins.parsers.ntriples import NTriplesParser
else:
    from rdflib.plugins.parsers.ntriples import W3CNTriplesParser as NTriplesParser


# NTriplesParser.nodeid changed its function signature between 5.0.0 and 6.0.0.
if rdflib.__version__ < "6":

    def _preserving_nodeid(self):
        if not self.peek("_"):
            return False
        return bNode(self.eat(r_nodeid).group(1))


else:

    def _preserving_nodeid(self, bnode_context=None):
        if not self.peek("_"):
            return False
        return bNode(self.eat(r_nodeid).group(1))


NTriplesParser.nodeid = _preserving_nodeid
# .. and accept bnodes everywhere
_uriref = NTriplesParser.uriref


def _uriref_or_nodeid(self):
    return _uriref(self) or self.nodeid()


NTriplesParser.uriref = _uriref_or_nodeid


TC_BASE = "http://json-ld.org/test-suite/tests/"


def do_test_json(cat, num, inputpath, expectedpath, context, options):
    base = TC_BASE + inputpath
    input_obj = _load_json(inputpath)
    input_graph = ConjunctiveGraph()
    to_rdf(
        input_obj,
        input_graph,
        base=base,
        context_data=context,
        produce_generalized_rdf=True,
    )
    expected_json = _load_json(expectedpath)
    use_native_types = True  # CONTEXT in input_obj
    result_json = from_rdf(
        input_graph,
        context,
        base=TC_BASE + inputpath,
        use_native_types=options.get("useNativeTypes", use_native_types),
        use_rdf_type=options.get("useRdfType", False),
    )

    def _prune_json(data):
        if CONTEXT in data:
            data.pop(CONTEXT)
        if GRAPH in data:
            data = data[GRAPH]
        # def _remove_empty_sets(obj):
        return data

    expected_json = _prune_json(expected_json)
    result_json = _prune_json(result_json)

    _compare_json(expected_json, result_json)


def do_test_parser(cat, num, inputpath, expectedpath, context, options):
    input_obj = _load_json(inputpath)
    expected_graph = _load_nquads(expectedpath)
    base = TC_BASE + inputpath
    result_graph = ConjunctiveGraph()
    to_rdf(
        input_obj,
        result_graph,
        base=base,
        context_data=context,
        produce_generalized_rdf=options.get("produceGeneralizedRdf", False),
    )
    assert isomorphic(result_graph, expected_graph), "Expected:\n%s\nGot:\n%s" % (
        expected_graph.serialize(format="turtle"),
        result_graph.serialize(format="turtle"),
    )


def do_test_serializer(cat, num, inputpath, expectedpath, context, options):
    input_graph = _load_nquads(inputpath)
    expected_json = _load_json(expectedpath)
    result_json = from_rdf(
        input_graph,
        context,
        base=TC_BASE + inputpath,
        use_native_types=options.get("useNativeTypes", False),
        use_rdf_type=options.get("useRdfType", False),
    )
    _compare_json(expected_json, result_json)


def _load_nquads(source):
    graph = ConjunctiveGraph()
    with open(source) as f:
        data = f.read() if IS_PY3 else f.read().decode("utf-8")
    graph.parse(data=data, format="nquads")
    return graph


def _load_json(source):
    with open(source) as f:
        return json.load(f)


def _to_ordered(obj):
    if isinstance(obj, list):
        # NOTE: use type in key to handle mixed
        # lists of e.g. bool, int, float.
        return sorted(
            (_to_ordered(lv) for lv in obj),
            key=lambda x: (_ord_key(x), type(x).__name__),
        )
    if not isinstance(obj, dict):
        return obj
    return sorted((k, _to_ordered(v)) for k, v in obj.items())


def _ord_key(x):
    if isinstance(x, dict) and "@id" in x:
        return x["@id"]
    else:
        return x


def _dump_json(obj):
    return json.dumps(
        obj, indent=4, separators=(",", ": "), sort_keys=True, check_circular=True
    )


def _compare_json(expected, result):
    expected = json.loads(_dump_json(expected))
    result = json.loads(_dump_json(result))
    assert _to_ordered(expected) == _to_ordered(
        result
    ), "Expected JSON:\n%s\nGot:\n%s" % (_dump_json(expected), _dump_json(result))

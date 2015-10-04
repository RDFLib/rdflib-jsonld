from __future__ import with_statement
from os import environ, chdir, path as p
try:
    import json
    assert json
except ImportError:
    import simplejson as json
from rdflib import ConjunctiveGraph, Graph, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib.py3compat import PY3
import rdflib_jsonld.parser
from rdflib_jsonld.parser import to_rdf
from rdflib_jsonld.serializer import from_rdf
from rdflib_jsonld.keys import CONTEXT, GRAPH


rdflib_jsonld.parser.ALLOW_LISTS_OF_LISTS = False

# monkey-patch NTriplesParser to keep source bnode id:s ..
from rdflib.plugins.parsers.ntriples import NTriplesParser, r_nodeid, bNode
def _preserving_nodeid(self):
    if not self.peek('_'):
        return False
    return bNode(self.eat(r_nodeid).group(1))
NTriplesParser.nodeid = _preserving_nodeid
# .. and accept bnodes everywhere
_uriref = NTriplesParser.uriref
def _uriref_or_nodeid(self):
    return _uriref(self) or self.nodeid()
NTriplesParser.uriref = _uriref_or_nodeid


unsupported_tests = ("frame", "normalize")
unsupported_tests += ("error", "remote",)
unsupported_tests += ("flatten", "compact", "expand")

known_bugs = (
        # invalid nquads (bnode as predicate)
        #"toRdf-0078-in", "toRdf-0108-in",
        # TODO: Literal doesn't preserve representations
        "fromRdf-0002-in", "toRdf-0035-in", "toRdf-0101-in",
        "fromRdf-0008-in", # TODO: needs to disallow outer lists-of-lists
        #"toRdf-0091-in", # TODO: multiple aliases version?
        )

import sys
if sys.version_info[:2] < (2, 6):
    # Fails on bug in older urlparse.urljoin; ignoring..
    known_bugs += ('toRdf-0069-in','toRdf-0102-in')

TC_BASE = "http://json-ld.org/test-suite/tests/"


testsuite_dir = environ.get("JSONLD_TESTSUITE") or p.join(
        p.abspath(p.dirname(__file__)), "test-suite")
test_dir = p.join(testsuite_dir, "tests")


def read_manifest(skiptests):
    f = open(p.join(testsuite_dir, "manifest.jsonld"), 'r')
    manifestdata = json.load(f)
    f.close()
    # context = manifestdata.get('context')
    for m in manifestdata.get('sequence'):
        if any(token in m for token in unsupported_tests):
            continue
        f = open(p.join(testsuite_dir, m), 'r')
        md = json.load(f)
        f.close()
        for test in md.get('sequence'):
            parts = test.get(u'input', '').split('.')[0].split('-')
            category, testnum, direction = parts
            if test.get(u'input', '').split('.')[0] in skiptests \
                or category in skiptests:
                pass
            else:
                inputpath = test.get(u'input')
                expectedpath = test.get(u'expect')
                context = test.get(u'context', False)
                options = test.get(u'option') or {}
                yield category, testnum, inputpath, expectedpath, context, options


def test_suite(skip_known_bugs=True):
    skiptests = unsupported_tests
    if skip_known_bugs:
        skiptests += known_bugs
    chdir(test_dir)
    for cat, num, inputpath, expectedpath, context, options in read_manifest(skiptests):
        if inputpath.endswith(".jsonld"): # toRdf
            if expectedpath.endswith(".jsonld"): # compact/expand/flatten
                func = _test_json
            else: # toRdf
                func = _test_parser
        else:  # fromRdf
            func = _test_serializer
        #func.description = "%s-%s-%s" % (group, case)
        yield func, cat, num, inputpath, expectedpath, context, options


def _test_json(cat, num, inputpath, expectedpath, context, options):
    base = TC_BASE + inputpath
    input_obj = _load_json(inputpath)
    input_graph = ConjunctiveGraph()
    to_rdf(input_obj, input_graph, base=base, context_data=context,
            produce_generalized_rdf=True)
    expected_json = _load_json(expectedpath)
    use_native_types = True # CONTEXT in input_obj
    result_json = from_rdf(input_graph, context, base=TC_BASE + inputpath,
            use_native_types=options.get('useNativeTypes', use_native_types),
            use_rdf_type=options.get('useRdfType', False))

    def _prune_json(data):
        if CONTEXT in data:
            data.pop(CONTEXT)
        if GRAPH in data:
            data = data[GRAPH]
        #def _remove_empty_sets(obj):
        return data

    expected_json = _prune_json(expected_json)
    result_json = _prune_json(result_json)

    _compare_json(expected_json, result_json)


def _test_parser(cat, num, inputpath, expectedpath, context, options):
    input_obj = _load_json(inputpath)
    expected_graph = _load_nquads(expectedpath)
    base = TC_BASE + inputpath
    result_graph = ConjunctiveGraph()
    to_rdf(input_obj, result_graph, base=base, context_data=context,
            produce_generalized_rdf = options.get('produceGeneralizedRdf', False))
    assert isomorphic(
            result_graph, expected_graph), "Expected:\n%s\nGot:\n%s" % (
            expected_graph.serialize(format='turtle'),
            result_graph.serialize(format='turtle'))


def _test_serializer(cat, num, inputpath, expectedpath, context, options):
    input_graph = _load_nquads(inputpath)
    expected_json = _load_json(expectedpath)
    result_json = from_rdf(input_graph, context, base=TC_BASE + inputpath,
            use_native_types=options.get('useNativeTypes', False),
            use_rdf_type=options.get('useRdfType', False))
    _compare_json(expected_json, result_json)


def _load_nquads(source):
    graph = ConjunctiveGraph()
    with open(source) as f:
        if PY3:
            data = f.read()
        else:
            data = f.read().decode('utf-8')
    graph.parse(data=data, format='nquads')
    return graph


def _load_json(source):
    with open(source) as f:
        return json.load(f)


def _to_ordered(obj):
    if isinstance(obj, list):
        # NOTE: use type in key to handle mixed
        # lists of e.g. bool, int, float.
        return sorted((_to_ordered(lv) for lv in obj),
                key=lambda x: (_ord_key(x), type(x).__name__))
    if not isinstance(obj, dict):
        return obj
    return sorted((k, _to_ordered(v))
            for k, v in obj.items())


def _ord_key(x):
    if isinstance(x, dict) and '@id' in x:
        return x['@id']
    else:
        return x


def _dump_json(obj):
    return json.dumps(obj,
            indent=4, separators=(',', ': '),
            sort_keys=True, check_circular=True)


def _compare_json(expected, result):
    expected = json.loads(_dump_json(expected))
    result = json.loads(_dump_json(result))
    assert _to_ordered(expected) == _to_ordered(result), \
            "Expected JSON:\n%s\nGot:\n%s" % (
                    _dump_json(expected), _dump_json(result))

if __name__ == '__main__':
    import sys
    from rdflib import *
    from datetime import datetime

    EARL = Namespace("http://www.w3.org/ns/earl#")
    DC = Namespace("http://purl.org/dc/terms/")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    DOAP = Namespace("http://usefulinc.com/ns/doap#")

    rdflib_jsonld_page = "https://github.com/RDFLib/rdflib-jsonld"
    rdflib_jsonld = URIRef(rdflib_jsonld_page + "#it")

    args = sys.argv[1:]
    asserter = URIRef(args.pop(0)) if args else None
    asserter_name = Literal(args.pop(0)) if args else None

    graph = Graph()

    graph.parse(data="""
        @prefix earl: <{EARL}> .
        @prefix dc: <{DC}> .
        @prefix foaf: <{FOAF}> .
        @prefix doap: <{DOAP}> .

        <{rdflib_jsonld}> a doap:Project, earl:TestSubject, earl:Software ;
            doap:homepage <{rdflib_jsonld_page}> ;
            doap:name "RDFLib-JSONLD" ;
            doap:programming-language "Python" ;
            doap:title "RDFLib plugin for JSON-LD " .
    """.format(**vars()), format='turtle')

    if asserter_name:
        graph.add((asserter, RDF.type, FOAF.Person))
        graph.add((asserter, FOAF.name, asserter_name))
        graph.add((rdflib_jsonld, DOAP.developer, asserter))

    for args in test_suite(skip_known_bugs=False):
        try:
            args[0](*args[1:])
            success = True
        except AssertionError:
            success = False
        assertion = graph.resource(BNode())
        assertion.add(RDF.type, EARL.Assertion)
        assertion.add(EARL.mode, EARL.automatic)
        if asserter:
            assertion.add(EARL.assertedBy, asserter)
        assertion.add(EARL.subject, rdflib_jsonld)
        assertion.add(EARL.test, URIRef(
            "http://json-ld.org/test-suite/tests/{1}-manifest.jsonld#t{2}".format(*args)))
        result = graph.resource(BNode())
        assertion.add(EARL.result, result)
        result.add(RDF.type, EARL.TestResult)
        result.add(DC.date, Literal(datetime.utcnow()))
        result.add(EARL.outcome, EARL.passed if success else EARL.failed)

    graph.serialize(sys.stdout, format='turtle')

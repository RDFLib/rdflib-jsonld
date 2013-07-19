from os import environ, chdir, path as p
try:
    import json
    assert json
except ImportError:
    import simplejson as json
from rdflib import ConjunctiveGraph
from rdflib.compare import isomorphic
from rdflib.py3compat import PY3
from rdflib_jsonld.parser import to_rdf
from rdflib_jsonld.serializer import from_rdf


# monkey-patch NTriplesParser to keep source bnode id:s
from rdflib.plugins.parsers.ntriples import NTriplesParser, r_nodeid, b, bNode
def nodeid(self):
    if not self.peek(b('_')):
        return False
    return bNode(self.eat(r_nodeid).group(1).decode())
NTriplesParser.nodeid = nodeid


skiptests = (
    "compact",
    "expand",
    "frame",
    "normalize",
    "fromRdf-0012-in", # TODO: circular list; fix graph.items circular loop bug
    # TODO: check use_native_types for integer and double reprs
    "toRdf-0035-in",
    "toRdf-0101-in",
    # TODO: test needs update
    "toRdf-0089-in", # .. subject strings not auto-coerced to @id
    # invalid nquads (bnode as graph name)
    "toRdf-0060-in",
    "toRdf-0061-in",
    # invalid nquads (bnode as predicate)
    "toRdf-0078-in",
    "toRdf-0108-in",
    # TODO: contentious?
    "toRdf-0065-in", # "_" as term, curie as raw term..
    "toRdf-0091-in", # very indirected terms..
    "toRdf-0102-in", # /.././useless/../../
    )


TC_BASE = "http://json-ld.org/test-suite/tests/"


testsuite_dir = environ.get("JSONLD_TESTSUITE") or p.join(
        p.dirname(__file__), "test-suite")
test_dir = p.join(testsuite_dir, "tests")
manifest_path = "test-suite/manifest.jsonld"


def read_manifest():
    f = open(p.join(p.dirname(__file__), manifest_path), 'r')
    manifestdata = json.load(f)
    f.close()
    # context = manifestdata.get('context')
    for m in manifestdata.get('sequence'):
        if 'Rdf' in m:
            f = open(m.split('/')[-1], 'r')
            md = json.load(f)
            f.close()
            for test in md.get('sequence'):
                category, testnum, direction = test.get(
                                u'input', '').split('.')[0].split('-')
                if test.get(u'input', '').split('.')[0] in skiptests \
                    or category in skiptests:
                    pass
                else:
                    inputpath = test.get(u'input')
                    expectedpath = test.get(u'expect')
                    context = test.get(u'context', False)
                    yield category, testnum, inputpath, expectedpath, context


def test_suite():
    chdir(test_dir)
    for group, case, inputpath, expectedpath, context in read_manifest():
        if inputpath.endswith(".jsonld"):  # toRdf
            func = _test_parser
        else:  # fromRdf
            func = _test_serializer
        #func.description = "%s-%s-%s" % (group, case)
        yield func, inputpath, expectedpath, context


def _test_parser(inputpath, expectedpath, context):
    input_obj = _load_json(inputpath)
    expected_graph = _load_nquads(expectedpath)
    base = TC_BASE + inputpath
    result_graph = ConjunctiveGraph()
    to_rdf(input_obj, result_graph, base=base, context_data=context)
    assert isomorphic(
            result_graph, expected_graph), "Expected:\n%s\nGot:\n%s" % (
            expected_graph.serialize(format='turtle'),
            result_graph.serialize(format='turtle'))


def _test_serializer(inputpath, expectedpath, context):
    input_graph = _load_nquads(inputpath)
    expected_json = _load_json(expectedpath)
    result_json = from_rdf(input_graph, context, base=TC_BASE + inputpath)
    _compare_json(expected_json, result_json)


def _load_nquads(source):
    f = open(source)
    try:
        graph = ConjunctiveGraph()
        if PY3:
            data = f.read()
        else:
            data = f.read().decode('utf-8'
                ).encode('latin-1')  # FIXME: bug in rdflib
        graph.parse(data=data, format='nquads')
        return graph
    finally:
        f.close()


def _load_json(source):
    f = open(source)
    try:
        return json.load(f)
    finally:
        f.close()


def _to_ordered(obj):
    if isinstance(obj, list):
        # NOTE: use type in key to handle mixed
        # lists of e.g. bool, int, float.
        return sorted((_to_ordered(lv) for lv in obj),
                key=lambda x: (_ord_key(x), type(x).__name__))
    if not isinstance(obj, dict):
        return obj
    return dict((k, _to_ordered(v))
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
    expected = _to_ordered(json.loads(_dump_json(expected)))
    result = _to_ordered(json.loads(_dump_json(result)))
    if not isinstance(expected, list):
        expected = [expected]
    if not isinstance(result, list):
        result = [result]
    assert expected == result, "Expected JSON:\n%s\nGot:\n%s" % (
            _dump_json(expected), _dump_json(result))

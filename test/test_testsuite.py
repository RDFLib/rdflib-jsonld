from os import chdir, path as p
try:
    import json
    assert json
except ImportError:
    import simplejson as json
from rdflib import ConjunctiveGraph
from rdflib.compare import isomorphic
from rdflib_jsonld.jsonld_parser import to_rdf
from rdflib_jsonld.jsonld_serializer import to_tree


skiptests = (
    "compact",
    "expand",
    "frame",
    "normalize",
    # "fromRdf",
    "fromRdf-0012-in", # TODO: circular list; fix graph.items circular loop bug
    # "toRdf",
    # "toRdf-0005-in",
    # "toRdf-0016-in",
    # "toRdf-0017-in",
    # "toRdf-0018-in",
    # "toRdf-0027-in",
    # "toRdf-0028-in",
    # "toRdf-0029-in",
    # "toRdf-0030-in",
    )


test_dir = p.join(p.dirname(__file__), 'test-suite/tests')


TC_BASE = "http://json-ld.org/test-suite/tests/"


def read_manifest():
    f = open(p.join(p.dirname(__file__), 'test-suite/manifest.jsonld'), 'r')
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
        if inputpath.endswith(".jsonld"): # toRdf
            func = _test_parser
        else: # fromRdf
            func = _test_serializer
        #func.description = "%s-%s-%s" % (group, case)
        yield func, inputpath, expectedpath, context


def _test_parser(inputpath, expectedpath, context):
    input_tree = _load_json(inputpath)
    expected_graph = _load_nquads(expectedpath)
    base = TC_BASE + inputpath
    result_graph = to_rdf(input_tree, ConjunctiveGraph(), base=base, context_data=context)
    assert isomorphic(result_graph, expected_graph), "Expected:\n%s\nGot:\n%s" % (
            expected_graph.serialize(format='n3'),
            result_graph.serialize(format='n3'))


def _test_serializer(inputpath, expectedpath, context):
    input_graph = _load_nquads(inputpath)
    expected_json = open(expectedpath).read()
    #if context is False:
    #    context = test_tree.get('@context')
    result_json = input_graph.serialize(format="json-ld", context=context)
    _compare_json(expected_json, result_json)


def _load_nquads(source):
    try:
        f = open(source)
        graph = ConjunctiveGraph()
        data = f.read().decode('utf-8').encode('latin-1') # FIXME: bug in rdflib
        graph.parse(data=data, format='nquads')
        return graph
    finally:
        f.close()

def _load_json(source):
    try:
        f = open(source)
        return json.load(f)
    finally:
        f.close()


def _to_ordered(obj):
    if not isinstance(obj, dict):
        return obj
    out = {}
    for k, v in obj.items():
        if isinstance(v, list):
            # NOTE: use type in key to handle mixed
            # lists of e.g. bool, int, float.
            v = sorted((_to_ordered(lv) for lv in v),
                    key=lambda x: (x, type(x).__name__))
        else:
            v = _to_ordered(v)
        out[k] = v
    return out


def _dump_json(tree):
    return json.dumps(tree,
            indent=4, separators=(',', ': '),
            sort_keys=True, check_circular=True)


def _compare_json(expected, result):
    expected = _to_ordered(json.loads(expected))
    result = _to_ordered(json.loads(result))
    if not isinstance(expected, list): expected = [expected]
    if not isinstance(result, list): result = [result]
    assert expected == result, "Expected JSON:\n%s\nGot:\n%s" % (
            _dump_json(expected), _dump_json(result))

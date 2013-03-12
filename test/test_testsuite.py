from os import chdir, path as p
from rdflib.py3compat import PY3
if PY3:
    from io import StringIO
import logging
try:
    import json
    assert json
except ImportError:
    import simplejson as json
from rdflib import ConjunctiveGraph
from rdflib.compare import isomorphic
from rdflib_jsonld.jsonld_parser import to_rdf
from rdflib_jsonld.jsonld_serializer import to_tree

log = logging.getLogger(__name__)

## Skip all tests

skiptests = (
    "compact",
    "expand",
    "frame",
    # "fromRdf",
    "normalize",
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

# 'base': 'http://json-ld.org/test-suite/tests/' + test['input']}


def read_manifest():
    f = open(p.join(p.dirname(__file__), 'test-suite/manifest.jsonld'), 'r')
    manifestdata = json.load(f)
    f.close()
    # context = manifestdata.get('context')
    for m in manifestdata.get('sequence'):
        if 'Rdf' in m:
            f = open(m.split('/')[-1], 'r')
            md = json.load(StringIO(f.read()) if PY3 else f)
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
                    yield inputpath, expectedpath, context


def test_suite():
    chdir(test_dir)
    for inputpath, expectedpath, context in read_manifest():
        yield _test_serializer, inputpath, expectedpath, context, "Serializer"
        yield _test_parser, inputpath, expectedpath, context, "Parser"


def _test_parser(inputpath, expectedpath, context, serpar):
    test_tree, test_graph = _load_test_data(inputpath, expectedpath, context)
    if isinstance(test_tree, ConjunctiveGraph):
        graph = test_tree
    else:
        g = ConjunctiveGraph()
        result = to_rdf(test_tree, g, context_data=context)
    if test_graph is not None:
        assert isomorphic(result, test_graph), \
            "Expected:\n%s\nGot:\n%s" % (
                test_graph.serialize(format='n3'),
                result.serialize(format='n3'))
        # assert isomorphic(graph, test_graph), \
        #         "Mismatch of expected graph vs result"
    else:
        graph_json = graph.serialize(format="json-ld", context=context)
        expected_json = open(expectedpath, 'rb').read()
        assert jsonld_compare(graph_json, expected_json) == True, \
                "Expected JSON:\n%s\nGot:\n %s" % (expected_json, graph_json)


def _test_serializer(inputpath, expectedpath, context, serpar):
    test_tree, test_graph = _load_test_data(inputpath, expectedpath, context)

    if isinstance(test_tree, ConjunctiveGraph):
        expected = test_tree.serialize(format="json-ld")
    else:
        expected = _to_json(_to_ordered(test_tree))

    if test_graph is not None:
        # toRdf, expected are nquads
        result_tree = to_tree(test_graph, context_data=context)
        result = _to_json(_to_ordered(result_tree))

    elif inputpath.startswith('fromRdf'):
        # fromRdf, expected in json-ld
        g = ConjunctiveGraph()
        data = open(p.join(test_dir, inputpath), 'rb').read()
        g.parse(data=data, format="nquads", context=context)
        result = g.serialize(format="json-ld", base=context)

    else:
        # json
        f = open(p.join(test_dir, inputpath), 'rb')
        result = json.load(f)[0]
        f.close()

    if isinstance(result, ConjunctiveGraph):
        assert isomorphic(result, expected), \
            "Expected graph of %s:\n%s\nGot graph of %s:\n %s" % (
                expected.serialize(format='n3'),
                result.serialize(format='n3'))
    else:
        assert jsonld_compare(expected, result) == True, \
                "Expected JSON:\n%s\nGot:\n%s" % (expected, result)


def _load_test_data(inputpath, expectedpath, context):
    test_tree = _load_test_inputpath(inputpath, expectedpath, context)
    test_graph = _load_test_expectedpath(inputpath, expectedpath, context)
    return test_tree, test_graph


def _load_test_expectedpath(inputpath, expectedpath, context):
    if '.jsonld' in expectedpath:
        test_graph = None
    elif '.nq' in expectedpath:
        test_graph = ConjunctiveGraph()
        test_graph.parse(expectedpath, format='nquads', publicId=context)
    else:
        raise Exception("expectedpath %s" % expectedpath)
    return test_graph


def _load_test_inputpath(inputpath, expectedpath, context):
    if '.jsonld' in inputpath:
        f = open(inputpath, 'rb')
        test_tree = json.load(
            StringIO(f.read().decode('utf-8')) if PY3 else f)
        f.close()
    elif '.nq' in inputpath:
        test_tree = ConjunctiveGraph()
        test_tree.parse(inputpath, format='nquads')
    else:
        raise Exception("Unable to load test_data from %s" % inputpath)
    return test_tree


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


def _to_json(tree):
    return json.dumps(tree,
            indent=4, separators=(',', ': '),
            sort_keys=True, check_circular=True)


def jsonld_compare(expected, result):
    if isinstance(expected, str if PY3 else basestring):
        expected = json.loads(StringIO(expected).read() if PY3 else expected)
    else:
        expected = json.loads(StringIO(expected.decode('utf-8')
                    ).read() if PY3 else expected)
    if isinstance(result, str if PY3 else basestring):
        result = json.loads(StringIO(result).read() if PY3 else result)
    else:
        result = json.loads(StringIO(result.decode('utf-8')
                    ).read()if PY3 else result)
    expected = expected[0] if isinstance(expected, list) else expected
    result = result[0] if isinstance(result, list) else result
    return len(expected) == len(result)


if __name__ == "__main__":
    test_suite()

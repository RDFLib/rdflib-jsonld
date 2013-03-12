from glob import glob
from os import path as p
import json

from rdflib import Graph
from rdflib.compare import isomorphic
# from rdfextras.ldcontext import Context
from rdflib_jsonld.jsonld_parser import to_rdf
from rdflib_jsonld.jsonld_serializer import to_tree


test_dir = p.join(p.dirname(__file__), 'tests')


def path_pairs():
    for turtlepath in glob(p.join(test_dir, '*.ttl')):
        commonpath = p.splitext(turtlepath)[0]
        yield commonpath + '.jsonld', turtlepath


def test_jsonld():
    for jsonpath, turtlepath in path_pairs():
        yield _test_serializer, jsonpath, turtlepath
        yield _test_parser, jsonpath, turtlepath


def _test_serializer(jsonpath, turtlepath):
    test_tree, test_graph = _load_test_data(jsonpath, turtlepath)

    src_context = test_tree.get('@context')
    result_tree = to_tree(test_graph, src_context, None, False)

    expected = _to_json(_to_ordered(test_tree))
    result = _to_json(_to_ordered(result_tree))
    assert expected == result, \
            "Expected JSON:\n%s\nGot:\n %s" % (expected, result)


def _test_parser(jsonpath, turtlepath):
    test_tree, test_graph = _load_test_data(jsonpath, turtlepath)
    graph = to_rdf(test_tree, Graph())
    assert isomorphic(graph, test_graph), \
            "Expected graph:\n%s\nGot:\n %s" % (
                    test_graph.serialize(format='n3'),
                    graph.serialize(format='n3'))


# def _load_test_data(jsonpath, turtlepath):
#     with open(jsonpath) as f:
#         test_tree = json.load(f)
#     test_graph = Graph().parse(turtlepath, format='n3')
#     return test_tree, test_graph


def _load_test_data(jsonpath, turtlepath):
    f = open(jsonpath, 'r')
    test_tree = json.load(f)
    test_graph = Graph().parse(turtlepath, format='n3')
    f.close()
    return test_tree, test_graph


#def _sparql_to_turtle(sparql):
#    ttl = re.sub(r'(?i)PREFIX\s+([^>]+>)', r'@prefix \1 .', sparql)
#    ttl = re.sub(r'(?si)ASK\s+WHERE\s*{(.*)}', r'\1', ttl)
#    ttl = re.sub(r'\?(\w+)', r'_:\1', ttl)
#    if not ttl.rstrip().endswith("."):
#        ttl += " ."
#    return ttl


def _to_ordered(obj):
    if not isinstance(obj, dict):
        return obj
    out = {}
    for k, v in obj.items():
        if isinstance(v, list):
            # NOTE: use type in key to handle mixed lists of
            # e.g. bool, int, float.
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

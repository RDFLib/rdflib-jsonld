import os
import sys
from random import choice
from nose.exc import SkipTest
import rdflib
import logging
log = logging.getLogger(__file__)


skiptests = {
    'example3': "C++ style comment causes parse exception",
}


class Envelope(object):
    def __init__(self, n, f):
        self.name = n
        self.file = f

    def __repr__(self):
        return self.name


def genericbadjsontest(e):
    """Documentation"""
    if e.skip is not None:
        raise SkipTest("%s skipped, %s" % (e.name, e.skip))
    g = rdflib.Graph()
    try:
        g.parse(e.file, format="json-ld")
        assert True is False
    except ValueError:
        assert True is True


def generictest(e):
    """Documentation"""
    if e.skip is not None:
        raise SkipTest("%s skipped, %s" % (e.name, e.skip))
    gjson = rdflib.Graph()
    gn3 = rdflib.Graph()
    gjson.parse(e.file + '.json', format="json-ld")
    gn3.parse(e.file + '.nt', format="nt")
    log.debug(gjson.serialize(format="nt"))
    log.debug(gn3.serialize(format="nt"))
    (s, p, o) = choice(list(gn3.triples((None, None, None))))
    assert gjson.subjects(p, o) is not None


def test_cases():
    from copy import deepcopy
    allfiles = os.listdir(os.getcwd() + '/test/json')
    badfiles = [f for f in allfiles if f.startswith('bad')]
    examples = [f.split('.')[0]
                    for f in allfiles
                    if f.startswith('example') and f.endswith('.json')]
    for tfile in set(badfiles):
        gname = tfile.split('.')[0]
        e = Envelope(gname, os.getcwd() + '/test/json/' + tfile)
        if gname in skiptests:
            e.skip = skiptests[gname]
        else:
            e.skip = None
        # e.skip = True
        if sys.version_info[:2] == (2, 4):
            import pickle
            gbjt = pickle.dumps(genericbadjsontest)
            gt = pickle.loads(gbjt)
        else:
            gt = deepcopy(genericbadjsontest)
        gt.__doc__ = tfile
        yield gt, e
    for example in examples:
        gname = example.split('.')[0]
        e = Envelope(gname, os.getcwd() + '/test/json/' + example)
        if gname in skiptests:
            e.skip = skiptests[gname]
        else:
            e.skip = None
        gt = deepcopy(generictest)
        gt.__doc__ = tfile
        yield gt, e


if __name__ == "__main__":
    test_cases()

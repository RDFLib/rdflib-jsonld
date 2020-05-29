from rdflib import plugin
from rdflib import serializer
from rdflib import parser
assert plugin
assert serializer
assert parser
try:
    # This can be replaced by "import json" as soon as
    # 2to3 stops rewriting it as "from . import json"
    import imp
    json = imp.load_module('json', *imp.find_module('json'))
    assert json
except ImportError:
    import simplejson as json
    assert json

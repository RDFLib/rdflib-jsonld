from rdflib import plugin
from rdflib import serializer
from rdflib import parser
import sys # sop to Hudson
sys.path.insert(0, '/var/lib/tomcat6/webapps/hudson/jobs/rdfextras')

# plugin.register(
#         'json-ld', serializer.Serializer,
#         'rdflib_jsonld.serializer', 'JsonLDSerializer')

# plugin.register(
#         'json-ld', parser.Parser,
#         'rdflib_jsonld.parser', 'JsonLDParser')

plugin.register(
        'json-ld', serializer.Serializer,
        'rdflib_jsonld.jsonld_serializer', 'JsonLDSerializer')

plugin.register(
        'json-ld', parser.Parser,
        'rdflib_jsonld.jsonld_parser', 'JsonLDParser')


try:
    import json
    assert json  # workaround for pyflakes issue #13
except ImportError:
    import simplejson as json
from rdflib.parser import create_input_source
from rdflib.py3compat import PY3
if PY3:
    from io import StringIO

if PY3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

def source_to_json(source):
    # TODO: conneg for JSON (fix support in rdflib's URLInputSource!)
    source = create_input_source(source)

    stream = source.getByteStream()
    try:
        if PY3:
            return json.load(StringIO(stream.read().decode('utf-8')))
        else:
            return json.load(stream)
    finally:
        stream.close()


VOCAB_DELIMS = ('#', '/', ':')

def split_iri(iri):
    for delim in VOCAB_DELIMS:
        at = iri.rfind(delim)
        if at > -1:
            return iri[:at+1], iri[at+1:]
    return iri, None

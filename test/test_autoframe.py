from rdflib_jsonld.autoframe import autoframe

data = {
    "@context": {"@vocab": "http://schema.org/", "@base": "http://example.net/"},
    "@graph": [
        {
            "@id": "/work/1",
            "@type": "CreativeWork",
            "name": "The Work",
            "hasPart": [
                {"@id": "/part/1"},
                {"@id": "/part/2"},
                {"@id": "/part/3"}
            ]
        },
        {
            "@id": "/part/1",
            "@type": "MediaObject",
            "name": "Part 1",
            "isPartOf": {"@id": "/work/1"},
            "creator": {"@id": "/person/1"}
        },
        {
            "@id": "/part/2",
            "@type": "MediaObject",
            "name": "Part 2",
            "creator": {"@id": "/person/1"}
        },
        {
            "@id": "/person/1",
            "@type": "Person",
            "name": "Some One"
        },
        {
            "@id": "/dataset",
            "@type": "Dataset",
            "name": "The Set",
            "hasPart": [{"@id": "/work/1"}, {"@id": "/work/2"}]
        },
        {
            "@id": "/work/2",
            "@type": "CreativeWork",
            "name": "Other Work",
            "creator": {"@id": "/person/1"}
        }
    ]
}

framed = autoframe(data, "/work/1")

import json
print json.dumps(framed, indent=2, separators=(',', ': '), sort_keys=True,
        ensure_ascii=False).encode('utf-8')

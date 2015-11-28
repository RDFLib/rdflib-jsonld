#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re

# Ridiculous as it may seem, we need to import multiprocessing and logging here
# in order to get tests to pass smoothly on python 2.7.
try:
    import multiprocessing
    import logging
except:
    pass


def setup_python3():
    # Taken from "distribute" setup.py
    from distutils.filelist import FileList
    from distutils import dir_util, file_util, util, log
    from os.path import join

    tmp_src = join("build", "src")
    # log.set_verbosity(1)
    fl = FileList()
    for line in open("MANIFEST.in"):
        if not line.strip():
            continue
        fl.process_template_line(line)
    dir_util.create_tree(tmp_src, fl.files)
    outfiles_2to3 = []
    for f in fl.files:
        outf, copied = file_util.copy_file(f, join(tmp_src, f), update=1)
        if copied and outf.endswith(".py"):
            outfiles_2to3.append(outf)

    util.run_2to3(outfiles_2to3)

    # arrange setup to use the copy
    sys.path.insert(0, tmp_src)

    return tmp_src


# Find version. We have to do this because we can't import it in Python 3 until
# its been automatically converted in the setup process.
def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)

__version__ = find_version('rdflib_jsonld/__init__.py')

install_requires = ["rdflib>=4.0", ] 

if sys.version_info[:2] < (2, 6):
    install_requires += ["simplejson"]

config = dict(
    name = 'rdflib-jsonld',
    description = "rdflib extension adding JSON-LD parser and serializer",
    maintainer = "RDFLib Team",
    maintainer_email = "http://groups.google.com/group/rdflib-dev",
    url = "https://github.com/RDFLib/rdflib-jsonld",
    version = __version__,
    download_url = "https://github.com/RDFLib/rdflib-jsonld/zipball/master",
    license = "BSD",
    platforms = ["any"],
    long_description = \
    """
    This parser/serialiser will

    * read in an JSON-LD formatted document and create an RDF graph
    * serialize an RDF graph to JSON-LD formatted output

    See:

        http://json-ld.org/
    """,
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Natural Language :: English",
                   ],
    packages = ["rdflib_jsonld"],
    test_suite = "test",
    install_requires = ["rdflib>=4.2"],
    entry_points = {
        'rdf.plugins.parser': [
            'json-ld = rdflib_jsonld.parser:JsonLDParser',
            'application/ld+json = rdflib_jsonld.parser:JsonLDParser',
        ],
        'rdf.plugins.serializer': [
            'json-ld = rdflib_jsonld.serializer:JsonLDSerializer',
            'application/ld+json = rdflib_jsonld.serializer:JsonLDSerializer',
        ],
    }
)

if sys.version_info[0] >= 3:
    from setuptools import setup
    config.update({'use_2to3': True})
    config.update({'src_root': setup_python3()})
else:
    try:
        from setuptools import setup
        config.update({'test_suite' : "nose.collector"})
    except ImportError:
        from distutils.core import setup


setup(**config)

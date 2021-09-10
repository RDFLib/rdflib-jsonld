#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import re

from os.path import dirname
from setuptools import setup

ROOT = dirname(__file__)

RE_REQUIREMENT = re.compile(r"^\s*-r\s*(?P<filename>.*)$")

RE_MD_CODE_BLOCK = re.compile(r"```(?P<language>\w+)?\n(?P<lines>.*?)```", re.S)
RE_SELF_LINK = re.compile(r"\[(.*?)\]\[\]")
RE_LINK_TO_URL = re.compile(r"\[(?P<text>.*?)\]\((?P<url>.*?)\)")
RE_LINK_TO_REF = re.compile(r"\[(?P<text>.*?)\]\[(?P<ref>.*?)\]")
RE_LINK_REF = re.compile(r"^\[(?P<key>[^!].*?)\]:\s*(?P<url>.*)$", re.M)
RE_TITLE = re.compile(r"^(?P<level>#+)\s*(?P<title>.*)$", re.M)
CUT = "<!-- CUT HERE -->"

RST_TITLE_LEVELS = ["=", "-", "*"]


def md2pypi(filename):
    """
    Load .md (markdown) file and sanitize it for PyPI.
    Remove unsupported github tags:
     - travis ci build badges
    """
    content = io.open(filename).read().split(CUT)[0]

    for match in RE_MD_CODE_BLOCK.finditer(content):
        rst_block = "\n".join(
            [".. code-block:: {language}".format(**match.groupdict()), ""]
            + ["    {0}".format(l) for l in match.group("lines").split("\n")]
            + [""]
        )
        content = content.replace(match.group(0), rst_block)

    refs = dict(RE_LINK_REF.findall(content))
    content = RE_LINK_REF.sub(".. _\g<key>: \g<url>", content)
    content = RE_SELF_LINK.sub("`\g<1>`_", content)
    content = RE_LINK_TO_URL.sub("`\g<text> <\g<url>>`_", content)

    for match in RE_LINK_TO_REF.finditer(content):
        content = content.replace(
            match.group(0),
            "`{text} <{url}>`_".format(
                text=match.group("text"), url=refs[match.group("ref")]
            ),
        )

    for match in RE_TITLE.finditer(content):
        underchar = RST_TITLE_LEVELS[len(match.group("level")) - 1]
        title = match.group("title")
        underline = underchar * len(title)

        full_title = "\n".join((title, underline))
        content = content.replace(match.group(0), full_title)

    return content


name = "rdflib-jsonld"
version = __import__("rdflib_jsonld").__version__


setup(
    name=name,
    version=version,
    description="rdflib extension adding JSON-LD parser and serializer",
    long_description=md2pypi("README.md"),
    maintainer="RDFLib Team",
    maintainer_email="rdflib-dev@google.com",
    url="https://github.com/RDFLib/rdflib-jsonld",
    license="BSD",
    packages=["rdflib_jsonld"],
    zip_safe=False,
    platforms=["any"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    test_suite="nose.collector",
    install_requires=["rdflib"],
    tests_require=["nose"],
    command_options={
        "build_sphinx": {
            "project": ("setup.py", name),
            "version": ("setup.py", ".".join(version.split(".")[:2])),
            "release": ("setup.py", version),
        }
    },
    entry_points={
        "rdf.plugins.parser": [
            "json-ld = rdflib_jsonld.parser:JsonLDParser",
            "application/ld+json = rdflib_jsonld.parser:JsonLDParser",
        ],
        "rdf.plugins.serializer": [
            "json-ld = rdflib_jsonld.serializer:JsonLDSerializer",
            "application/ld+json = rdflib_jsonld.serializer:JsonLDSerializer",
        ],
    },
)

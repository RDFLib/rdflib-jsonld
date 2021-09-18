"""
"""
__version__ = "0.6.2"

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("default")
    warnings.warn(
        "The rdflib-jsonld package has been integrated into rdflib as of rdflib==6.0.1.  "
        "Please remove rdflib-jsonld from your project's dependencies.",
        DeprecationWarning,
    )

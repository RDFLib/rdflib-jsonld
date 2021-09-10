"""
"""
__version__ = "0.6.0"

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("default")
    warnings.warn(
        "The rdflib-jsonld package has been integrated into rdflib as of rdflib==6.0.0.  "
        "Please remove rdflib-jsonld from your project's dependencies.",
        DeprecationWarning,
    )

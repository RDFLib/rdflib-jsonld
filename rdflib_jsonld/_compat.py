import sys

IS_PY3 = sys.version_info[0] >= 3

basestring = str if IS_PY3 else basestring  # noqa
unicode = str if IS_PY3 else unicode  # noqa

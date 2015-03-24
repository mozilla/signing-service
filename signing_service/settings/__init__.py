from .base import *  # flake8: noqa

try:
    from .local import *  # flake8: noqa
except ImportError, exc:
    exc.args = tuple(['%s (did you rename settings/local.py-dist?)'
                      % exc.args[0]])
    raise exc

from .base import *  # noqa

# Any settings here will override the base settings but only while runnning the
# test suite.

SECRET_KEY = ('Imma let you finish but this is one of the best test '
              'suites of all time')

SKIP_HAWK_AUTH = True

HAWK_CREDENTIALS = {
    'signing-service': {
        'id': 'signing-service',
        'key': 'some long random string',
        'algorithm': 'sha256'
    }
}

# This lets Nose capture logging.
del LOGGING['loggers']['hawkrest']
del LOGGING['loggers']['mohawk']

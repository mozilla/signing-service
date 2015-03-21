"""
Django settings for signing_service project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import logging.handlers
import cef
import tempfile

from collections import OrderedDict

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# You must set a secret key in local settings.
SECRET_KEY = ''

DEBUG = False
TEMPLATE_DEBUG = False

# On production, this must contain the hostname of the Django app.
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Third-party apps, patches, fixes
    'raven.contrib.django',
    'rest_framework',
    'hawkrest',

    # Local apps
    'signing_service.base',
    'signing_service.system',
)

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    'django_paranoia.sessions.ParanoidSessionMiddleware',
    'hawkrest.middleware.HawkResponseMiddleware',
)

ROOT_URLCONF = 'signing_service.urls'

WSGI_APPLICATION = 'signing_service.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# This app does not use a database but declaring some settings seems to help
# out a few pesky things.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


# Custom settings.

STATSD_CLIENT = 'django_statsd.clients.normal'


DJANGO_PARANOIA_REPORTERS = [
    'django_paranoia.reporters.cef_',
]

SESSION_ENGINE = 'django_paranoia.sessions'


SYSLOG_TAG = 'http_app_signing_service'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'base': {
            '()': 'logging.Formatter',
            'format': '%(name)s:%(levelname)s '
                      '%(message)s :%(pathname)s:%(lineno)s'
        },
        'cef': {
            '()': cef.SysLogFormatter,
            'datefmt': '%H:%M:%s',
        }
    },
    'handlers': {
        'unicodesyslog': {
            '()': 'mozilla_logger.log.UnicodeHandler',
            'facility': logging.handlers.SysLogHandler.LOG_LOCAL7,
            'formatter': 'base',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            '()': logging.StreamHandler,
            'formatter': 'base',
        },
        'cef_syslog': {
            '()': logging.handlers.SysLogHandler,
            'facility': logging.handlers.SysLogHandler.LOG_LOCAL4,
            'formatter': 'cef',
        },

    },
    'loggers': {
        '': {
            'handlers': ['unicodesyslog'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['unicodesyslog', 'sentry'],
            'level': 'INFO',
            'propagate': True
        },
        'cef': {
            'handlers': ['cef_syslog']
        },
        'hawkrest': {
            'handlers': ['unicodesyslog'],
            'level': 'INFO',
            'propagate': True,
        },
        'mohawk': {
            'handlers': ['unicodesyslog'],
            # Set this to DEBUG for any Hawk auth debugging.
            'level': 'INFO',
            'propagate': True,
        },
        'boto': {
            'handlers': ['unicodesyslog'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

SENTRY_DSN = ''

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'hawkrest.HawkAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'limit'
}

# CEF logging.

CEF_DEFAULT_SEVERITY = 5
CEF_PRODUCT = 'Signing-Service'
CEF_VENDOR = 'Mozilla'
CEF_VERSION = '0'
CEF_DEVICE_VERSION = '0'

# Should robots.txt allow web crawlers? We set this to False since it's a
# private API.
ENGAGE_ROBOTS = False

# Common test runner settings.
# Note: you must put django_nose in your INSTALLED_APPS (in local settings)
# for these to take affect.

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--logging-clear-handlers',
    '--with-nicedots',
    '--with-blockage',
    '--http-whitelist=""',
]

# When True, it means Hawk authentication will be disabled everywhere.
# This is mainly just to get a speed-up while testing.
SKIP_HAWK_AUTH = False

HAWK_CREDENTIALS = {
    # These credentials are for requests the Marketplace to communicate
    # with the signing-service.
    'marketplace-signing': {
        'id': 'marketplace-signing',
        # Set this to some long random string.
        'key': '',
        'algorithm': 'sha256'
    },
}

# Number of seconds until a Hawk message expires.
HAWK_MESSAGE_EXPIRATION = 60

# When True, use the Django cache framework for checking Hawk nonces.
# Django must already be configured to use some kind of caching backend.
USE_CACHE_FOR_HAWK_NONCE = True

# Various options for the signing process.
# The default testing value is the RHS

# Which particular type of signing does this instance of the signing service
# support?  For anything but dev testing, this should probably be just one
# of the three.
SIGNING_SERVICE_WE_ARE_SIGNING = (
    'apps',
    'addons',
    'receipts'
)

# Which OpenSSL engine to use, if any.
# For apps and addons production(and probably stage) cases this should be set
# to 'chil'
SIGNING_SERVICE_ENGINE = ''

# Receipt signing specific options

# The PEM formatted private key.  In production this is a "magic" file that
# tells the HSM which stored key to use.  In testing, it should be a normal
# RSA private key.  The PEM file should not be encrypted.  a.k.a. no passphrase
SIGNING_SERVICE_RECEIPTS_KEY_FILE = os.path.join(BASE_DIR, 'receipts',
                                                 'tests', 'assets',
                                                 'test_key.pem')

# The JWK-in-a-JWT "certificate" that is included with the receipt's JWT.
SIGNING_SERVICE_RECEIPTS_CERT_FILE = os.path.join(BASE_DIR, 'receipts',
                                                  'tests', 'assets',
                                                  'test_crt.jwk')

# A list of permitted issuers that we are signing for.  This list should be
# a  http://, https://, or app:// URLs
SIGNING_SERVICE_RECEIPTS_ISSUERS = (
    'https://marketplace-dev.allizom.org',
)

# End of receipt signing specific options

# FirefoxOS privileged app signing specific options

# PEM formatted RSA private key.  See comments about
# SIGNING_SERVICE_RECEIPTS_KEY_FILE above for information on formatting.
SIGNING_SERVICE_APPS_KEY_FILE = os.path.join(BASE_DIR, 'apps', 'tests',
                                             'assets', 'apps_test_key.pem')

# PEM formatted X.509 certificate used for signing.
SIGNING_SERVICE_APPS_CERT_FILE = os.path.join(BASE_DIR, 'apps', 'tests',
                                              'assets', 'apps_test_cert.pem')

# CA chain for the signing certificate.  This file likely has one, possibly
# two PEM formatted X.509 certificates for CAs.  The order of these
# certificates should be the same as the order of certification, i.e. the
# CA that issued the signing certificate should be first and the ultimate root
# cert should be last.  It is possible that these are one and the same
# certificate.
SIGNING_SERVICE_APPS_CA_CHAIN_FILE = os.path.join(BASE_DIR, 'apps',
                                                  'tests', 'assets',
                                                  'apps_test_cert.pem')

# End of app signing specific options

# Addons signing specific options

# The path to the PEM formatted RSA private key.  This key is the issuing CA's
# private key that will be used to issue the one-time-use key and certificate
# pairs that are created for each addon signing request.  See comments about
# SIGNING_SERVICE_RECEIPTS_KEY_FILE above for information on formatting.
SIGNING_SERVICE_ADDONS_CA_KEY_FILE = os.path.join(BASE_DIR, 'addons',
                                                  'tests', 'assets',
                                                  'addons_test_root_ca_key.pem')  # noqa

# The certificate for the CA that will be issuing the one-time-use keys
SIGNING_SERVICE_ADDONS_CA_CERT_FILE = os.path.join(BASE_DIR, 'addons',
                                                   'tests', 'assets',
                                                   'addons_test_root_ca_cert.pem')  # noqa

# The length of the generated one-time-use signing keys in bits.  2048 is the
# lower bound on this for production.  In testing, something as small as 512
# can be used but on modern hardware there should be no perceivable difference.
SIGNING_SERVICE_ADDONS_KEY_SIZE = 2048

# The validity period of the generated one-time-use signing certificates.
# Default to 10 yaers.
SIGNING_SERVICE_ADDONS_LIFETIME = 3650

# Which digest algorithm to use.  We really shouldn't be using anything
# weaker than SHA256.
SIGNING_SERVICE_ADDONS_DIGEST_ALGO = 'sha256'

# The distinguished name(DN) template that will be used when generating the
# signing certificates.  The final portion of the DN, the common name(CN)
# attribute, is populated with the identifier of the addon that is passed in
# as part of the signing request.
SIGNING_SERVICE_ADDONS_BASE_DN = OrderedDict([
    ('C', 'US'),
    ('ST', 'Denial'),
    ('L', 'Calvinville'),
    ('O',  'Allizom, Cni.'),
    ('OU', 'Jerrymandering')
])

#
SIGNING_SERVICE_ADDONS_CERT_EXTENSIONS = {
    'basicConstraints': 'CA:false',
    'subjectKeyIdentifier': 'hash',
    'authorityKeyIdentifier': 'keyid:always',
    'keyUsage': 'digitalSignature'
}

# End of addons signing specific options

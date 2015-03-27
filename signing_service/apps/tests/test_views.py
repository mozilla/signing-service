import base64
import os

from django.test import TestCase

from rest_framework.test import APIRequestFactory

from signing_service.apps.views import AppsView

from websigning.tests.base import der_to_pkcs7, get_signature_cert_subject


def test_file(fname):
    return os.path.join(os.path.dirname(__file__), 'assets', fname)
test_file.__test__ = False  # noqa

VIEW = AppsView.as_view()
FACTORY = APIRequestFactory()


class AppsViewTest(TestCase):

    def test_no_get(self):
        request = FACTORY.get('/1.0/sign_app')
        response = VIEW(request)
        self.assertEqual(response.status_code, 405)

    def test_no_file(self):
        request = FACTORY.post('/1.0/sign_app', {})
        response = VIEW(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error']['file'][0],
                         u'This field is required.')

    def test_broken_body(self):
        with open(test_file('broken_signature')) as f:
            request = FACTORY.post('/1.0/sign_app', {'file': f})
        response = VIEW(request)
        self.assertEqual(response.data['error']['file'][0],
                         u'Unrecognized line format: "Beebop"')

    def test_correct_body(self):
        with open(test_file('signature')) as f:
            request = FACTORY.post('/1.0/sign_app', {'file': f})
        response = VIEW(request)

        signature = base64.b64decode(response.data['signature.rsa'])
        #
        # DO NOT MAKE THE FOLLOWING TWO LINES A ONE LINER
        #
        # M2Crypto appears to have a race condition that gets very angry if
        # you do.
        pkcs7 = der_to_pkcs7(signature)
        signature_subject = get_signature_cert_subject(pkcs7)
        self.assertEqual(str(signature_subject),
                         '/C=UN/ST=Denial/L=Calvinville'
                         '/O=Sprinting Llamas, Inc.'
                         '/CN=Llama Operations Group')

import base64
import os
import tempfile

from django.test import TestCase

from rest_framework.test import APIRequestFactory

from signing_service.addons.views import AddonsView

from websigning.tests.base import der_to_pkcs7, get_signature_cert_subject


def test_file(fname):
    return os.path.join(os.path.dirname(__file__), 'assets', fname)
test_file.__test__ = False  # noqa


class AddonsViewTest(TestCase):

    def setUp(self):
        self.view = AddonsView.as_view()
        self.factory = APIRequestFactory()

    def test_01_no_get(self):
        request = self.factory.get('/1.0/sign_addon')
        response = self.view(request)
        self.assertEqual(response.status_code, 405)

    def test_02_missing_addon_id(self):
        with open(test_file('signature')) as f:
            request = self.factory.post('/1.0/sign_addon', {'file': f})
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'],
                         {'addon_id': [u'This field is required.']})

    def test_03_short_addon_id(self):
        with open(test_file('signature')) as f:
            request = self.factory.post('/1.0/sign_addon',
                                        {'file': f, 'addon_id': 'yes'})
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'],
                         {'addon_id': [u'Ensure this value has at least 4 '
                                       u'characters (it has 3).']})

    def test_04_long_addon_id(self):
        with open(test_file('signature')) as f:
            request = self.factory.post('/1.0/sign_addon',
                                        {'file': f, 'addon_id': '0' * 150})
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'],
                         {'addon_id': [u'Ensure this value has at most 128 '
                                       u'characters (it has 150).']})

    def test_05_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=True) as f:
            request = self.factory.post('/1.0/sign_addon',
                                        {'addon_id': 'beebop', 'file': f})
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'],
                         {'file': [u'The submitted file is empty.']})

    def test_06_broken_body(self):
        with open(test_file('broken_signature')) as f:
            request = self.factory.post('/1.0/sign_addon',
                                        {'file': f, 'addon_id': 'Beebop'})
        response = self.view(request)
        self.assertEqual(response.data['error'],
                         {'file': [u'Unrecognized line format: "Beebop"']})

    def test_07_correct_body(self):
        with open(test_file('signature')) as f:
            request = self.factory.post('/1.0/sign_addon',
                                        {'file': f, 'addon_id': 'Beebop'})
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

        signature = base64.b64decode(response.data['signature.rsa'])

        #
        # DO NOT MAKE THE FOLLOWING TWO LINES A ONE LINER
        #
        # M2Crypto appears to have a race condition that gets very angry if
        # you do.
        pkcs7 = der_to_pkcs7(signature)
        signature_subject = get_signature_cert_subject(pkcs7)
        self.assertEqual(str(signature_subject),
                         '/C=US/ST=Denial/L=Calvinville'
                         '/O=Allizom, Cni.'
                         '/OU=Jerrymandering'
                         '/CN=Beebop')

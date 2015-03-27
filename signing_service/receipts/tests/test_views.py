import os

import jwt

from django.test import TestCase

from rest_framework.test import APIRequestFactory

from signing_service.receipts.views import ReceiptsView


def test_file(fname):
    return os.path.join(os.path.dirname(__file__), 'assets', fname)
test_file.__test__ = False  # noqa


class ReceiptsViewTest(TestCase):

    def setUp(self):
        self.view = ReceiptsView.as_view()
        self.factory = APIRequestFactory()
        with open(test_file('test_crt.jwk')) as f:
            self.issuer = jwt.decode(f.read(), verify=False)

    def test_no_get(self):
        request = self.factory.get('/1.0/sign')
        response = self.view(request)
        self.assertEqual(response.status_code, 405)

    def test_no_body(self):
        request = self.factory.post('/1.0/sign')
        response = self.view(request)
        self.assertEqual(response.status_code, 400)

    def test_empty_json(self):
        request = self.factory.post('/1.0/sign', {})
        response = self.view(request)
        self.assertEqual(response.status_code, 400)

    def test_incorrect_json(self):
        request = self.factory.post('/1.0/sign', {'b': 'a'}, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'],
                         'Required key "detail" missing')

    def test_correct_receipt(self):
        receipt = {"typ": "purchase-receipt",
                   "product": {"url": "https://grumpybadgers.com",
                               "storedata": "5169314356"},
                   "user": {"type": "email",
                            "value": "pickles@example9.com"},
                   "iss": "https://marketplace-dev.allizom.org",
                   "nbf": self.issuer['iat'],
                   "iat": self.issuer['iat'],
                   "detail": "https://appstore.com/receipt/5169314356",
                   "verify": "https://appstore.com/verify/5169314356"}
        request = self.factory.post('/1.0/sign', receipt, format='json')
        response = self.view(request)
        certificate, signed_receipt = response.data['receipt'].split('~')
        self.assertEqual(receipt, jwt.decode(signed_receipt, verify=False))

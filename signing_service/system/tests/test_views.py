from django.core.urlresolvers import reverse

from mock import patch
from nose.tools import eq_

from signing_service.base.tests import TestCase


class TestAuthView(TestCase):

    def test_get(self):
        res = self.client.get(reverse('system.auth'))
        self.assert2x(res)
        eq_(self.json(res),
            {'message': 'GET authentication successful'})

    def test_post(self):
        res = self.client.post(reverse('system.auth'))
        self.assert2x(res)
        eq_(self.json(res),
            {'message': 'POST authentication successful'})


class TestCEFView(TestCase):

    @patch('signing_service.system.views.log_cef')
    def test(self, cef):
        eq_(self.json(self.client.get(reverse('system.cef'))),
            {'message': 'CEF messages sent'})
        assert cef.called


class TestLogView(TestCase):

    @patch('signing_service.system.views.log')
    def test(self, log):
        eq_(self.json(self.client.get(reverse('system.log'))),
            {'message': 'messages logged on server'})
        assert log.info.called
        assert log.error.called


class TestTraceView(TestCase):

    def test(self):
        with self.assertRaises(RuntimeError):
            self.client.post(reverse('system.trace'))


class TestStatsView(TestCase):

    @patch('signing_service.system.views.statsd')
    def test(self, statsd):
        self.assert2x(self.client.get(reverse('system.stats')))
        assert statsd.incr.called

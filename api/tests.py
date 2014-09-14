from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.authtoken.models import Token


import pprint; pp = pprint.PrettyPrinter()


class TestCompareLocation(TestCase):
    def setUp(self):
        self.mock_response = {}

    # @mock.patch()
    def test_returns_comparison(self):
        """The compare location API should return differences between crimes for a location and the city average"""
        lon = -122.64788229999999
        lat = 45.476296999999995
        url = '/api/v1.0/crimes/compare_location/{}/{}'.format(lon, lat)
        resp = self.client.get(url)
        print(resp.content)
        # pp.pprint(resp.data)
        self.assertTrue(False)


class TestCreateAuthTokenSignal(TestCase):
    def test_new_user_gets_token(self):
        """A new Django User should receive an API auth token"""
        User = get_user_model()
        u = User.objects.create_user(username="test", email="test@example.com", password="secret")
        expected = 1
        self.assertEqual(expected, Token.objects.filter(user=u).count())

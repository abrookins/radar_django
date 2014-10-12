import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.authtoken.models import Token

from crime_stats.tests import BaseCrimeTestCase


class TestCompareLocation(BaseCrimeTestCase):
    def setUp(self):
        self.mock_response = {}
        User = get_user_model()
        self.user = User.objects.create_user(username="test",
                                             email="test@example.com",
                                             password="secret")

    def test_returns_city_averages(self):
        """The compare location API should return city averages"""
        self.client.login(username="test", password="secret")
        lon = -122.64788229999999
        lat = 45.476296999999995
        url = '/api/v1.0/crimes/compare/{}/{}/to/city-average/'.format(lon, lat)
        resp = self.client.get(url)
        data = json.loads(resp.content.decode())

        expected_averages = {
            "Drugs": 3,
            "Gambling": 1,
            "DUII": 2,
            "Sex Offenses": 1,
            "Fraud": 2,
            "Rape": 1.0,
            "Stolen Property": 1,
            "Aggravated Assault": 2.0,
            "Burglary": 6.0,
            "Arson": 1,
            "Forgery": 2.0,
            "Vandalism": 6,
            "Weapons": 1.0,
            "Offenses Against Family": 1,
            "Robbery": 2.0,
            "Disorderly Conduct": 3,
            "Liquor Laws": 2,
            "Prostitution": 2,
            "Homicide": 1.0,
            "Larceny": 16,
            "Motor Vehicle Theft": 5,
            "Curfew": 1.0,
            "Trespass": 2.0,
            "Runaway": 1,
            "Assault, Simple": 3.0,
            "Kidnap": 1,
            "Embezzlement": 1
        }

        self.assertEqual(expected_averages, data['city_averages'])

    def test_returns_sum_of_crimes_by_crime_type_for_location(self):
        """The compare location API should return city averages"""
        self.client.login(username="test", password="secret")
        lon = -122.64788229999999
        lat = 45.476296999999995
        url = '/api/v1.0/crimes/compare/{}/{}/to/city-average/'.format(lon, lat)
        resp = self.client.get(url)
        data = json.loads(resp.content.decode())

        expected_sums = {
            'Assault, Simple': 3,
            'DUII': 3,
            'Motor Vehicle Theft': 7,
            'Vandalism': 10,
            'Forgery': 5,
            'Larceny': 53,
            'Trespass': 3,
            'Burglary': 6,
            'Disorderly Conduct': 3,
            'Drugs': 1
        }

        self.assertEqual(expected_sums, data['location_sums']['by_type'])


class TestCreateAuthTokenSignal(TestCase):
    def test_new_user_gets_token(self):
        """A new Django User should receive an API auth token"""
        User = get_user_model()
        u = User.objects.create_user(username="test", email="test@example.com",
                                     password="secret")
        expected = 1
        self.assertEqual(expected, Token.objects.filter(user=u).count())

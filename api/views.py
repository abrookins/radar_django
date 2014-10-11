from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from elasticsearch import Elasticsearch

from crime_stats import models, crime_averager, util


class CompareLocation(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        lat = float(kwargs['lat'])
        lon = float(kwargs['lon'])
        year = request.GET.get('year', 2013)
        precision = request.GET.get('precision', 6)

        es = Elasticsearch()

        crimes = models.Crimes(es, index=settings.CRIME_INDEX,
                               precision=precision)

        found_crimes = crimes.get_crimes_near_coordinate(lon, lat, year=year)
        crime_sums = util.get_crime_sums(found_crimes)

        # TODO: Average by hour and by day, since we have that data too.
        averager = crime_averager.CachingCrimeAverager(crimes=crimes,
                                                       root_dir=settings.DATA_DIR,
                                                       year=year)
        data = {
            'city_averages': averager.averages,
            'location_sums': crime_sums,
            'crime_types': averager.averages.keys()
        }

        return Response(data, status=status.HTTP_200_OK)


class CrimesNearLocation(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        lat = float(kwargs['lat'])
        lon = float(kwargs['lon'])
        year = request.GET.get('year', 2013)
        precision = request.GET.get('precision', 6)

        crimes = crimes.get_crimes_near_coordinate(lon, lat, precision=precision, year=year)
        crime_sums = crimes.get_crime_sums(crimes)

        return Response(crime_sums, status=status.HTTP_200_OK)


class CityAverages(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        year = request.GET.get('year', 2013)
        precision = request.GET.get('precision', 6)
        averager = models.CachingCrimeAverager(root_dir=settings.DATA_DIR, precision=precision, year=year)

        return Response(averager.averages, status=status.HTTP_200_OK)


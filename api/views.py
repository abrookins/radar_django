from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from crime_stats import util


class CompareLocation(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        lat = float(kwargs['lat'])
        lon = float(kwargs['lon'])
        year = request.GET.get('year', 2013)
        precision = request.GET.get('precision', 6)

        crimes = util.get_crimes_near_coordinate(lon, lat, precision=precision, year=year)
        crime_sums = util.get_crime_sums(crimes)
        sums_by_type = crime_sums['by_type']
        differences = {}

        # TODO: Average by hour and by day, since we have that data too.
        averager = util.CachingCrimeAverager(root_dir=settings.DATA_DIR, precision=precision, year=year)
        for crime_type, city_average in averager.averages.items():
            if crime_type in sums_by_type:
                type_sum_for_this_location = sums_by_type[crime_type]
            else:
                type_sum_for_this_location = 0

            difference = util.percentage_difference(city_average, type_sum_for_this_location)
            differences[crime_type] = difference

        return Response(differences, status=status.HTTP_200_OK)


class Crimes(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        lat = float(kwargs['lat'])
        lon = float(kwargs['lon'])
        year = request.GET.get('year', 2013)
        precision = request.GET.get('precision', 6)

        crimes = util.get_crimes_near_coordinate(lon, lat, precision=precision, year=year)
        crime_sums = util.get_crime_sums(crimes)

        return Response(crime_sums, status=status.HTTP_200_OK)


class CityAverages(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        year = request.GET.get('year', 2013)
        precision = request.GET.get('precision', 6)
        averager = util.CachingCrimeAverager(root_dir=settings.DATA_DIR, precision=precision, year=year)

        return Response(averager.averages, status=status.HTTP_200_OK)


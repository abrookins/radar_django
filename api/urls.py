from api.views import CompareLocation, CrimesNearLocation, CityAverages
from django.conf.urls import *

coordinates = '(?P<{}>(\-?\d+(\.\d+)?))/(?P<{}>(\-?\d+(\.\d+)?))'
lon_lat = coordinates.format('lon', 'lat')

urlpatterns = patterns('',
                       url(r'^v1.0/crimes/compare/{}/to/city-average/$'.format(lon_lat), CompareLocation.as_view(), name='compare_location'),
                       url(r'^v1.0/crimes/at_location/{}/$'.format(lon_lat), CrimesNearLocation.as_view(), name='crimes'),
                       url(r'^v1.0/crimes/city_averages/$', CityAverages.as_view(), name='crimes')
)

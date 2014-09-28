from api.views import CompareLocation, Crimes, CityAverages
from django.conf.urls import *


lon_lat = '(?P<lon>(\-?\d+(\.\d+)?))/(?P<lat>(\-?\d+(\.\d+)?))'

urlpatterns = patterns('',
                       url(r'^v1.0/crimes/compare_location/{}$'.format(lon_lat), CompareLocation.as_view(), name='compare_location'),
                       url(r'^v1.0/crimes/at_location/{}/$'.format(lon_lat), Crimes.as_view(), name='crimes'),
                       url(r'^v1.0/crimes/city_averages/$', CityAverages.as_view(), name='crimes')
)

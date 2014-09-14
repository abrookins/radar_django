from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       url('', include('django.contrib.auth.urls', namespace='auth')),
                       url('', include('social.apps.django_app.urls', namespace='social')),

                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),

                       url(r'^api/', include('api.urls', namespace='api')),
                       url(r'^$', 'accounts.views.home', name='home'),

                       url(r'^admin/', include(admin.site.urls)),
)

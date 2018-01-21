#-*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.landing, name='landing'),
    url(r'^home/$', views.index, name='index'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^GCID(?P<cid>[0-9]+)/$', views.detail, name='detail'),
#    url(r'^reference(?P<name_id>[0-9]+)/$', views.ref_detail, name='ref_detail'),
#    url(r'^references/$', views.references, name='references'),
#    url(r'^Coordinates_harris2010/$', views.Harris_2010_coordinates, name='Harris_2010_coordinates'),
#    url(r'^Metallicity_harris2010/$', views.Harris_2010_metallicity, name='Harris_2010_metallicity'),
#    url(r'^Velocities_harris2010/$', views.Harris_2010_velocities, name='Harris_2010_velocities'),
#    url(r'^register/$', views.register, name='register'),
#    url(r'^registered/$', views.registered, name='registered'),
#    url(r'^login/$', views.login, name='login'),
#    url(r'^logout/$', views.user_logout, name='logout'),
#    url(r'^submit/$', views.submit, name='submit'),
#    url(r'^submitted/$', views.submitted, name='submitted'),
#    url(r'^account/$', views.user_account, name='account'),
]

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.AddonsView.as_view(), name='sign_addon'),
)

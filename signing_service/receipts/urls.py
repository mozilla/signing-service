from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.ReceiptsView.as_view(), name='sign'),
)

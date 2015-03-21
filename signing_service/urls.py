from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'1.0/sign', include('signing_service.receipts.urls')),
    url(r'1.0/sign_app', include('signing_service.apps.urls')),
    url(r'1.0/sign_addons', include('signing_service.addons.urls')),
    url(r'system/', include('signing_service.system.urls')),
    url(r'', include('signing_service.base.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

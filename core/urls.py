from django.conf.urls import include
from django.conf.urls import url
from django.contrib.staticfiles.views import serve

from core import views as core_views

from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^service-worker.js', TemplateView.as_view(
            template_name="service-worker.js",
            content_type='application/javascript'),
        name='service-worker.js'),
    url(r'^gen/manifest.json', core_views.manifest, name='manifest'),
    url(r'^OneSignalSDKWorker.js', serve, kwargs={
            'path': 'js/OneSignalSDKWorker.js'}),
    url(r'^OneSignalSDKUpdaterWorker.js', serve, kwargs={
            'path': 'js/OneSignalSDKWorker.js'}),
    url(r'^terms/', include('termsandconditions.urls')),
]

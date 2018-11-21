from django.conf.urls import include
from django.conf.urls import url

from core import views as core_views


urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^gen/manifest.json', core_views.manifest, name='manifest'),
    url(r'^terms/', include('termsandconditions.urls')),
]

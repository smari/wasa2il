from django.conf.urls import include
from django.conf.urls import url

from core import views as core_views


urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^terms/', include('termsandconditions.urls')),
]

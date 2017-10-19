from django.conf.urls import url

from core import views as core_views


urlpatterns = [
    url(r'^$', core_views.home),
]

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from django.conf import settings

from core.views import *
from core import views as core_views
from core.ajax import *


urlpatterns = [
    url(r'^$', core_views.home),
]

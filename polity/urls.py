from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.generic import UpdateView

from polity.models import Polity
from polity.views import PolityCreateView
from polity.views import PolityDetailView
from polity.views import PolityListView


urlpatterns = [
    url(r'^polities/$', PolityListView.as_view()),
    url(r'^polity/new/$', login_required(PolityCreateView.as_view())),
    url(r'^polity/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
    url(r'^polity/(?P<pk>\d+)/(?P<action>\w+)/$', login_required(PolityDetailView.as_view())),
    url(r'^polity/(?P<pk>\d+)/$', never_cache(PolityDetailView.as_view()), name='polity'),
]

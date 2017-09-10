from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from django.conf import settings

from core.ajax.document import (
    document_propose, document_propose_change, render_markdown,
    documentcontent_render_diff
)
from core.views import *
from core import views as core_views
from core.ajax import *


urlpatterns = [
    url(r'^$', core_views.home),

    url(r'^search/$', SearchListView.as_view()),

    url(r'^polity/(?P<polity>\d+)/document/$', login_required(DocumentListView.as_view())),
    url(r'^polity/(?P<polity>\d+)/document/new/$', login_required(DocumentCreateView.as_view())),
    url(r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/$', DocumentDetailView.as_view()),
    # (r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/edit/$', login_required(DocumentUpdateView.as_view())),

    url(r'^api/document/propose/(?P<document>\d+)/(?P<state>\d+)/$', document_propose),
    url(r'^api/document/propose-change/$', document_propose_change),
    url(r'^api/document/render-markdown/$', render_markdown),

    url(r'^api/documentcontent/render-diff/$', documentcontent_render_diff),
]

from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, TemplateView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
	# Uncomment the admin/doc line below to enable admin documentation:
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),

	# Core app
	(r'^', include('wasa2il.core.urls')),
	(r'^accounts/profile/$', 'core.views.profile'),
	(r'^accounts/profile/(?P<user>.+)/$', 'core.views.profile'),
	(r'^accounts/', include('registration.urls')),

	(r'^help/$', direct_to_template, {"template": "help/index.html"}),
	(r'^help/(?P<page>.*)/$', "core.views.help"),

	(r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root': 'core/static/'}),
)

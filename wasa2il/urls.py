from django.conf.urls.defaults import patterns, include, url
from django.shortcuts import redirect
from django.conf import settings
from django.views.generic.simple import direct_to_template

from core.authentication import PiratePartyMemberAuthenticationForm

from django.contrib import admin
admin.autodiscover()

RSK_URL = 'https://www.island.is/audkenning?id=piratar.is'

login_url_params = {}
if 'core.authentication.PiratePartyMemberAuthenticationBackend' in settings.AUTHENTICATION_BACKENDS:
    login_url_params = { 'authentication_form': PiratePartyMemberAuthenticationForm }

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Enabling i18n language changes per
        # https://docs.djangoproject.com/en/1.4/topics/i18n/translation/#the-set-language-redirect-view
        (r'^i18n/', include('django.conf.urls.i18n')),

    # Core app
    (r'^', include('core.urls')),
    # Forums app
    (r'^', include('forum.urls')),

    (r'^accounts/profile/(?:(?P<username>.+)/)?$', 'core.views.profile'),
    (r'^accounts/settings/', 'core.views.view_settings'),
    # (r'^accounts/register/', lambda r: redirect(RSK_URL)),
    # (r'^accounts/login/', 'django.contrib.auth.views.login', login_url_params),
    (r'^accounts/login/', 'core.views.login', login_url_params),
    (r'^accounts/verify/', 'core.views.verify'),
    (r'^accounts/', include('registration.urls')),

    (r'^help/$', direct_to_template, {"template": "help/index.html"}),
    (r'^help/(?P<page>.*)/$', "core.views.help"),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root': settings.STATIC_ROOT}),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )

from django.conf.urls import patterns, include, url
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls import handler500
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from core.authentication import PiratePartyMemberAuthenticationForm

from django.contrib import admin

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
    # Gateway
    (r'^gateway/', include('gateway.urls')),

    (r'^accounts/profile/(?:(?P<username>.+)/)?$', 'core.views.profile'),
    url(r'^accounts/settings/', 'core.views.view_settings', name='account_settings'),
    # (r'^accounts/login/', 'django.contrib.auth.views.login', login_url_params),
    (r'^accounts/login/', 'core.views.login', login_url_params),
    (r'^accounts/verify/', 'core.views.verify'),
    (r'^accounts/sso/', 'core.views.sso'),

    # - START OF TEMPORARY COMPATIBILITY HACK -
    # IMPORTANT! The entire ^accounts/password/ section is here as a temporary hack until the official django-registration gets fixed!
    # See discussion: http://stackoverflow.com/questions/19985103/django-1-6-and-django-registration-built-in-authentication-views-not-picked-up
    # This may break in the future during an update of the django-registration package. Try removing this section.
    url(r'^accounts/password/change/$', auth_views.password_change, name='password_change'),
    url(r'^accounts/password/change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^accounts/password/reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    # - END OF TEMPORARY COMPATIBILITY HACK -

    (r'^accounts/', include('registration.urls')),

    (r'^help/$', TemplateView.as_view(template_name='help/is/index.html')),
    (r'^help/(?P<page>.*)/$', "core.views.help"),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root': settings.STATIC_ROOT}),
)

handler500 = 'core.views.error500'

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
    if 'debug_toolbar.apps.DebugToolbarConfig' in settings.INSTALLED_APPS:
        try:
            import debug_toolbar
            urlpatterns += patterns(
                '',
                url(r'^__debug__/', include(debug_toolbar.urls)),
            )
        except:
            pass

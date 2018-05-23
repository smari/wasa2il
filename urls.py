from django.conf.urls import include, url
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls import handler500
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.views import static

from registration.backends.default.views import RegistrationView

from core import views as core_views

from django.contrib import admin

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Enabling i18n language changes per
    # https://docs.djangoproject.com/en/1.4/topics/i18n/translation/#the-set-language-redirect-view
    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^', include('election.urls')),
    url(r'^', include('issue.urls')),
    url(r'^', include('core.urls')),
    url(r'^', include('polity.urls')),
    url(r'^', include('topic.urls')),
    # Gateway
    url(r'^gateway/', include('gateway.urls')),

    url(r'^accounts/profile/(?:(?P<username>[^/]+)/)?$', core_views.profile, name='profile'),
    url(r'^accounts/settings/', core_views.view_settings, name='account_settings'),
    url(r'^accounts/login/', core_views.Wasa2ilLoginView.as_view()),
    url(r'^accounts/sso/', core_views.sso),
    url(r'^accounts/register/$', core_views.Wasa2ilRegistrationView.as_view(), name='registration_register'),

    # SAML-related URLs.
    url(r'^accounts/verify/', core_views.verify),
    url(r'^accounts/login-or-saml-redirect/', core_views.login_or_saml_redirect),

    url(r'^accounts/', include('registration.urls')),

    url(r'^help/$', TemplateView.as_view(template_name='help/is/index.html')),
    url(r'^help/(?P<page>.*)/$', core_views.help),

    url(r'^static/(?P<path>.*)$', static.serve,  {'document_root': settings.STATIC_ROOT}),
]

if settings.FEATURES['tasks']:
    urlpatterns.append(url(r'^', include('tasks.urls')))


handler500 = 'core.views.error500'

if settings.DEBUG:
    urlpatterns += [
        url(r'^uploads/(?P<path>.*)$', static.serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
    if 'debug_toolbar.apps.DebugToolbarConfig' in settings.INSTALLED_APPS:
        try:
            import debug_toolbar
            urlpatterns += [
                url(r'^__debug__/', include(debug_toolbar.urls)),
            ]
        except:
            pass

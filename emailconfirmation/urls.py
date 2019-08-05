from django.conf.urls import url

from emailconfirmation.views import email_confirmation

urlpatterns = [
    url(r'^email-confirmation/(?P<key>[a-zA-Z0-9]{40})/$', email_confirmation, name='email_confirmation'),
]

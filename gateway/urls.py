from django.conf.urls import patterns

from gateway.register import PreverifiedRegistrationView


urlpatterns = patterns('',
    (r'^icepirate/adduser/$', 'gateway.icepirate.adduser'),
    (r'^register/$', PreverifiedRegistrationView.as_view())
)

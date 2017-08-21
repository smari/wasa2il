from django.conf.urls import url

from gateway.register import PreverifiedRegistrationView
from gateway import icepirate

urlpatterns = [
    url(r'^icepirate/adduser/$', icepirate.adduser),
    url(r'^register/$', PreverifiedRegistrationView.as_view())
]

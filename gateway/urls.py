from django.conf.urls import patterns

urlpatterns = patterns('',
    (r'^icepirate/adduser/$', 'gateway.icepirate.adduser')
)

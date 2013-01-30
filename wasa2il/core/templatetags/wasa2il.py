from core.models import *
from django import template

register = template.Library()

@register.filter(name='topicfavorited')
def topicfavorited(topic, user):
	try:
		ut = UserTopic.objects.get(user=user, topic=topic)
		return True
	except:
		return False


@register.filter(name='issuevoted')
def issuevoted(issue, user):
	try:
		ut = Vote.objects.get(user=user, issue=issue)
		print "FOO:", user, issue, ut.value
		if ut.value == 0:
			return False

		return True
	except Exception, e:
		print e
		return False

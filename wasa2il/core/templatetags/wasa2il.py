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

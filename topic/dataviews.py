from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from core.ajax.utils import jsonize
from core.models import UserProfile
from core.models import UserTopic

from polity.models import Polity

from topic.models import Topic


@login_required
@jsonize
def topic_star(request):
    ctx = {}
    topicid = int(request.GET.get('topic', 0))
    if not topicid:
        ctx["ok"] = False
        return ctx

    topic = get_object_or_404(Topic, id=topicid)

    ctx["topic"] = topic.id

    try:
        ut = UserTopic.objects.get(topic=topic, user=request.user)
        ut.delete()
        ctx["starred"] = False
    except UserTopic.DoesNotExist:
        UserTopic(topic=topic, user=request.user).save()
        ctx["starred"] = True

    topics = topic.polity.topic_set.listing_info(request.user)
    ctx["html"] = render_to_string("core/_topic_list_table.html", {"topics": topics, "user": request.user, "polity": topic.polity})

    ctx["ok"] = True

    return ctx


@login_required
@jsonize
def topic_showstarred(request):
    ctx = {}
    profile = UserProfile.objects.get(user=request.user)
    profile.topics_showall = not profile.topics_showall
    profile.save()

    ctx["showstarred"] = not profile.topics_showall

    polity = int(request.GET.get("polity", 0))
    if polity:
        try:
            polity = Polity.objects.get(id=polity)
            topics = polity.topic_set.listing_info(request.user)
            ctx["html"] = render_to_string("core/_topic_list_table.html", {"topics": topics, "user": request.user, "polity": polity})
        except Exception, e:
            ctx["error"] = e

    ctx["ok"] = True
    return ctx

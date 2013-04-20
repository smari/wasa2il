
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from core.models import Meeting, MeetingAgenda, MeetingIntervention, MOTION
from core.json.utils import jsonize, error


@login_required
@jsonize
def meeting_start(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    meeting.time_started = datetime.now()
    meeting.save()

    try:
        ag = meeting.meetingagenda_set.all().order_by("order")[0]
        ag.done = 1
        ag.save()
    except:
        pass

    return ctx


@login_required
@jsonize
def meeting_end(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    meeting.time_ended = datetime.now()
    meeting.save()

    return ctx


@login_required
@jsonize
def meeting_attend(request, meeting):
    ctx = {}

    meeting = get_object_or_404(Meeting, id=meeting)

    if not meeting.polity.is_member(request.user):
        ctx["ok"] = False
        return ctx

    meeting.attendees.add(request.user)
    ctx["ok"] = True
    return ctx


@login_required
@jsonize
def meeting_poll(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not meeting.polity.is_member(request.user):
        ctx["ok"] = False
        return ctx

    try:    time_starts = meeting.time_starts.strftime("%d/%m/%Y %H:%I")
    except:    time_starts = None
    try:    time_started = meeting.time_started.strftime("%d/%m/%Y %H:%I")
    except:    time_started = None
    try:    time_ends = meeting.time_ends.strftime("%d/%m/%Y %H:%I")
    except:    time_ends = None
    try:    time_ended = meeting.time_ended.strftime("%d/%m/%Y %H:%I")
    except:    time_ended = None

    ctx["polity"] = {"name": meeting.polity.name}
    ctx["meeting"] = {
        "called_by": meeting.user.username,
        "time_starts": time_starts,
        "time_starts_iso": str(meeting.time_starts),
        "time_started": time_started,
        "time_started_iso": str(meeting.time_started),
        "time_ends": time_ends,
        "time_ends_iso": str(meeting.time_ends),
        "time_ended": time_ended,
        "time_ended_iso": str(meeting.time_ended),
        "is_agenda_open": meeting.is_agenda_open,
        "is_not_started": meeting.notstarted(),
        "is_ongoing": meeting.ongoing(),
        "is_ended": meeting.ended(),
        "managers": [{'username': user.username, 'id': user.id, 'str': user.get_full_name() or str(user)} for user in meeting.managers.all()],
        "attendees": [user.username for user in meeting.attendees.all()],
        "user_is_manager": request.user in meeting.managers.all(),
        "user_is_attendee": request.user in meeting.attendees.all(),
        "agenda": [{"id": i.id, "item":i.item, "order":i.order, "done": i.done, "interventions":
            [{"user": x.user.username, "order": x.order, "motion": x.motion, "done": x.done}
            for x in i.meetingintervention_set.all()]}
            for i in meeting.meetingagenda_set.all().order_by("order")],
    }
    ctx["ok"] = True

    return ctx


@login_required
@jsonize
def meeting_agenda_add(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not meeting.polity.is_member(request.user):
        ctx["ok"] = False
        return ctx

    ag = MeetingAgenda()
    ag.meeting = meeting
    ag.item = request.REQUEST.get("item", "")
    try:
        ag.order = meeting.meetingagenda_set.all().order_by("-order")[0].order + 1
    except:
        ag.order = 1

    ag.done = 0
    ag.save()

    return meeting_poll(request)


@login_required
@jsonize
def meeting_agenda_remove(request):
    ctx = {}

    agendaid = int(request.REQUEST.get('item', 0))
    if not agendaid:
        ctx["ok"] = False
        return ctx

    agenda = get_object_or_404(MeetingAgenda, id=agendaid)

    if not agenda.meeting.id == int(request.REQUEST.get('meeting', 0)):
        ctx["ok"] = False
        return ctx

    if not agenda.meeting.polity.is_member(request.user):
        ctx["ok"] = False
        return ctx

    agenda.delete()

    return meeting_poll(request)


@login_required
@jsonize
def meeting_agenda_reorder(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not meeting.polity.is_member(request.user):
        ctx["ok"] = False
        return ctx

    order = request.REQUEST.getlist("order[]")
    for i in range(len(order)):
        agendaitem = MeetingAgenda.objects.get(id=order[i])
        agendaitem.order = i
        agendaitem.save()

    return meeting_poll(request)


@login_required
@jsonize
def meeting_agenda_open(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not request.user in meeting.managers.all():
        ctx["ok"] = False
        return ctx

    meeting.is_agenda_open = True
    meeting.save()

    return ctx


@login_required
@jsonize
def meeting_agenda_close(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not request.user in meeting.managers.all():
        ctx["ok"] = False
        return ctx

    meeting.is_agenda_open = False
    meeting.save()

    return ctx


@login_required
@jsonize
def meeting_agenda_next(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not request.user in meeting.managers.all():
        ctx["ok"] = False
        return ctx

    lastag = meeting.meetingagenda_set.filter(done=1)
    for ag in lastag:
        ag.done = 2
        ag.save()

    try:
        nextag = meeting.meetingagenda_set.filter(done=0).order_by("order")[0]
        nextag.done = 1
        nextag.save()
    except:
        pass

    return meeting_poll(request)


@login_required
@jsonize
def meeting_agenda_prev(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not request.user in meeting.managers.all():
        ctx["ok"] = False
        return ctx

    lastag = meeting.meetingagenda_set.filter(done=1)
    for ag in lastag:
        ag.done = 0
        ag.save()

    try:
        nextag = meeting.meetingagenda_set.filter(done=2).order_by("-order")[0]
        nextag.done = 1
        nextag.save()
    except:
        pass

    return meeting_poll(request)


@login_required
@jsonize
def meeting_intervention_next(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not request.user in meeting.attendees.all():
        ctx["ok"] = False
        return ctx

    try:
        meeting.meetingagenda_set.get(done=1)
    except:
        ctx["ok"] = False
        return ctx

    return meeting_poll(request)


@login_required
@jsonize
def meeting_intervention_prev(request):
    return meeting_poll(request)


@login_required
@jsonize
def meeting_intervention_add(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not request.user in meeting.attendees.all():
        ctx["ok"] = False
        return ctx

    motion = int(request.REQUEST.get('type', 0))
    if not motion:
        ctx["ok"] = False
        return ctx

    try:
        currentitem = meeting.meetingagenda_set.get(done=1)
    except:
        ctx["ok"] = False
        return ctx

    intervention = MeetingIntervention()
    intervention.meeting = meeting
    intervention.user = request.user
    intervention.motion = motion
    intervention.agendaitem = currentitem
    intervention.done = 0
    intervention.order = 1

    try:
        last_speaker = MeetingIntervention.objects.filter(agendaitem=currentitem).order_by('-order')[0]
    except IndexError:
        last_speaker = None
        if motion != MOTION['TALK']:
            return error('The first intervention must be a talk (FOR NOW)', ctx)
    else:

        same = last_speaker.user == request.user
        intervention.order = last_speaker.order + 1

        if motion == MOTION['TALK']:           # Request to talk

            if same and last_speaker.motion == MOTION['TALK']:
                return error('One cannot TALK twice in a row.')

        if motion == MOTION['REPLY']:           # Request to reply directly

            if same and last_speaker.motion in (MOTION['TALK'], MOTION['REPLY']):
                return error('One cannot REPLY to own\'s REPLY.')

            if last_speaker.motion not in (MOTION['TALK'], MOTION['REPLY'], ):
                return error('One can only REPLY to a TALK or another REPLY', ctx)

        elif motion == MOTION['CLARIFY']:        # Request to clarify

            raise NotImplementedError('This is not implemented now. TALK and REPLY should be enough for now.')

        elif motion == MOTION['POINT']:            # Request to make a point of order

            raise NotImplementedError('This is not implemented now. TALK and REPLY should be enough for now.')

    # Shift all existing interventions with greater-or-equal order
    for i in MeetingIntervention.objects.filter(agendaitem=currentitem, order__gte=intervention.order):
        i.order += 1
        i.save()

    # Finally save the new intervention
    intervention.save()

    return meeting_poll(request)


@login_required
@jsonize
def meeting_manager_add(request):
    ctx = {}

    meetingid = int(request.REQUEST.get('meeting', 0))
    if not meetingid:
        ctx["ok"] = False
        ctx['error'] = 'Meeting not found'
        return ctx

    meeting = get_object_or_404(Meeting, id=meetingid)

    if not request.user in meeting.managers.all():
        ctx["ok"] = False
        ctx['error'] = 'You are not a manger!'
        return ctx

    uq = request.REQUEST.get("user", "")
    try:
        u = User.objects.get(Q(username__iexact=uq) | Q(first_name__iexact=uq) | Q(last_name__iexact=uq))
        print u
    except User.DoesNotExist:
        ctx["ok"] = False
        ctx['error'] = 'User "%s" not found' % uq
        return ctx
    except User.MultipleObjectsReturned:
        ctx["ok"] = False
        ctx['error'] = 'Too many users found for query: %s' % uq
        return ctx

    if u in meeting.managers.all():
        ctx["ok"] = False
        ctx['error'] = 'User already a manger!'
        return ctx

    meeting.managers.add(u)

    return meeting_poll(request)


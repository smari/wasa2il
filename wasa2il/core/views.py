from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from core.models import *
from core.forms import *


def home(request):
	ctx = {}
	if request.user.is_authenticated():
		# Get some context vars (tempoarily just fetch the first one)
		ctx['allpolities'] = Polity.objects.filter(Q(is_listed=True) | Q(members=request.user))
		ctx['polities'] = Polity.objects.filter(members=request.user)
		# ctx['topics' ] = ctx['mainPolity'].topic_set.all()

		ctx["yourdocuments"] = Document.objects.filter(user=request.user)[:9]
		ctx["adopteddocuments"] = Document.objects.filter(is_adopted=True, polity__in=request.user.polity_set.all())[:9]
		ctx["proposeddocuments"] = Document.objects.filter(is_proposed=True, polity__in=request.user.polity_set.all())[:9]

		return render_to_response("home.html", ctx, context_instance=RequestContext(request))
	else:
		ctx['somepolities'] = Polity.objects.filter(is_listed=True).order_by("-id")[:4]

		return render_to_response("hom01.html", ctx, context_instance=RequestContext(request))


def help(request, page):
	return render_to_response("help/%s.html" % page)


def profile(request, user=None):
	ctx = {}
	if user:
		ctx["user"] = get_object_or_404(User, username=user)

	return render_to_response("profile.html", ctx, context_instance=RequestContext(request))


class TopicListView(ListView):
	context_object_name = "topics"
	template_name = "core/topic_list.html"

	def get_queryset(self):
		polity = get_object_or_404(Polity, polity=self.kwargs["polity"])
		return Topic.objects.filter(polity=polity)


class TopicCreateView(CreateView):
	context_object_name = "topic"
	template_name = "core/topic_form.html"
	form_class = TopicForm
	success_url="/polity/%(polity)d/topic/%(id)d/"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		self.success_url = "/polity/" + str(self.polity.id) + "/topic/%(id)d/"
		return super(TopicCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(TopicCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity})
		return context_data

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.polity = self.polity
		self.object.save()
		return HttpResponseRedirect(self.get_success_url())


class IssueCreateView(CreateView):
	context_object_name = "issue"
	template_name = "core/issue_form.html"
	form_class = IssueForm
	success_url="/issue/%(id)d/"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		return super(IssueCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(IssueCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity})
		return context_data

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.save()
		self.object.topics.add(self.topic)
		return HttpResponseRedirect(self.get_success_url())


class IssueDetailView(DetailView):
	model = Issue
	context_object_name = "issue"
	template_name = "core/issue_detail.html"

	def get_context_data(self, *args, **kwargs):
		context_data = super(IssueDetailView, self).get_context_data(*args, **kwargs)
		context_data.update({'comment_form': CommentForm()})
		return context_data


class PolityDetailView(DetailView):
	model = Polity
	context_object_name = "polity"
	template_name = "core/polity_detail.html"
	requested_membership = False
	membershiprequest = None

	def dispatch(self, *args, **kwargs):
		res = super(PolityDetailView, self).dispatch(*args, **kwargs)

		if kwargs.get("action") == "leave":
			self.object.members.remove(self.request.user)

		if kwargs.get("action") == "join":
			invite_threshold = self.object.get_invite_threshold()
			self.membershiprequest, self.requested_membership = MembershipRequest.objects.get_or_create(polity=self.object, requestor=self.request.user)

			# See if we have already satisfied the limits
			print self.membershiprequest.votes(), invite_threshold
			if self.membershiprequest.votes() >= invite_threshold and self.membershiprequest.left == False:
				self.object.members.add(self.request.user)
				self.membershiprequest.fulfilled = True
				self.membershiprequest.save()
		else:
			try:
				self.membershiprequest = MembershipRequest.objects.get(polity=self.object, requestor=self.request.user, pending=True)
			except:
				self.membershiprequest = None
			
		if self.request.user in self.object.members.all():
			self.membershiprequest = None

		res = super(PolityDetailView, self).dispatch(*args, **kwargs)

		return res
		

	def get_context_data(self, *args, **kwargs):
		ctx = {}
		context_data = super(PolityDetailView, self).get_context_data(*args, **kwargs)

		ctx['user_is_member'] = self.request.user in self.object.members.all()
		ctx["user_requested_membership"] = self.membershiprequest != None
		ctx["user_requested_membership_now"] = self.requested_membership
		ctx["membership_requests"] = MembershipRequest.objects.filter(polity=self.object, fulfilled=False)
		ctx["politytopics"] = self.object.get_topic_list(self.request.user)

		context_data.update(ctx)
		return context_data


class PolityCreateView(CreateView):
	model = Polity
	context_object_name = "polity"
	template_name = "core/polity_form.html"
	form_class = PolityForm
	success_url="/polity/%(id)d/"

	def form_valid(self, form):
		self.object = form.save()
		self.object.members.add(self.request.user)
		return super(PolityCreateView, self).form_valid(form)


class DocumentCreateView(CreateView):
	model = Document
	context_object_name = "document"
	template_name = "core/document_form.html"
	form_class = DocumentForm
	success_url="/document/%(id)d/"


	def dispatch(self, *args, **kwargs):
		try:
			self.issues = [get_object_or_404(Issue, id=kwargs["issue"])]
		except:
			self.issues = []
		try:
			self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		except:
			self.polity = None

		if len(self.issues) > 0 and not self.polity:
			self.polity = self.issues[0].polity

		return super(DocumentCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(DocumentCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity})
		context_data.update({'issues': self.issues})
		return context_data

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.polity = self.polity
		self.object.user = self.request.user
		self.object.save()
		for i in self.issues:
			self.object.issues.add(i)
		self.success_url = "/polity/" + str(self.polity.id) + "/document/" + str(self.object.id) + "/"
		return HttpResponseRedirect(self.get_success_url())


class DocumentDetailView(DetailView):
	model = Document
	context_object_name = "document"
	template_name = "core/document_detail.html"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		return super(DocumentDetailView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(DocumentDetailView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity})
		return context_data


class DocumentListView(ListView):
	model = Document
	context_object_name = "documents"
	template_name = "core/document_list.html"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		return super(DocumentListView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(DocumentListView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity})
		return context_data


class DocumentUpdateView(UpdateView):
	model = Document
	context_object_name = "document"
	template_name = "core/document_update.html"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		return super(DocumentUpdateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(DocumentUpdateView, self).get_context_data(*args, **kwargs)
		referabledocs = Document.objects.filter(is_adopted=True)
		print "Referabledocs: ", referabledocs

		context_data.update({'polity': self.polity, 'referabledocs': referabledocs})
		return context_data


class MeetingCreateView(CreateView):
	model = Meeting
	context_object_name = "meeting"
	template_name = "core/meeting_form.html"
	form_class = MeetingForm
	success_url="/polity/%(polity)d/meeting/%(id)d/"


	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		self.success_url = "/polity/" + str(self.polity.id) + "/meeting/$(id)d/"
		return super(MeetingCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(MeetingCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity})
		return context_data

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.polity = self.polity
		self.object.user = self.request.user
		self.object.save()
		self.object.managers.add(self.request.user)
		self.success_url = "/polity/" + str(self.polity.id) + "/meeting/" + str(self.object.id) + "/"
		return HttpResponseRedirect(self.get_success_url())


class MeetingDetailView(DetailView):
	model = Meeting
	context_object_name = "meeting"
	template_name = "core/meeting_detail.html"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		return super(MeetingDetailView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(MeetingDetailView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity, "now": datetime.now().strftime("%d/%m/%Y %H:%I")})
		return context_data


class MeetingListView(ListView):
	model = Meeting
	context_object_name = "meetings"
	template_name = "core/meeting_list.html"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		return super(MeetingListView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(MeetingListView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity})
		return context_data


class MeetingUpdateView(UpdateView):
	model = Meeting
	context_object_name = "meeting"
	template_name = "core/meeting_update.html"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		return super(MeetingUpdateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(MeetingUpdateView, self).get_context_data(*args, **kwargs)
		referabledocs = Meeting.objects.filter(is_adopted=True)
		print "Referabledocs: ", referabledocs

		context_data.update({'polity': self.polity, 'referabledocs': referabledocs})
		return context_data

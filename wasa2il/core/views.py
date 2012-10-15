from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import simplejson as json

from core.models import *
from core.forms import *

def jsonize(f):
        def wrapped(*args, **kwargs):
                return HttpResponse(json.dumps(f(*args, **kwargs)))

        return wrapped



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
	

		return render_to_response("hom01.html", ctx, context_instance=RequestContext(request))


def profile(request, user=None):
	ctx = {}
	if user:
		ctx["user"] = get_object_or_404(User, username=user)

	return render_to_response("profile.html", ctx, context_instance=RequestContext(request))

@login_required
@jsonize
def newstatement(request, polity, document, type):
	ctx = {}

	s = Statement()
	s.user = request.user
	s.document = get_object_or_404(Document, id=document)
	s.type = type
	try:
		s.number = Statement.objects.get(document=s.document, type=s.type).order_by('-number')[0].number + 1
	except:
		s.number = 1
	s.save()

	so = StatementOption()

	so.text = request.REQUEST.get("text", "")
	so.user = request.user
	so.save()
	s.text.add(so)

	ctx["ok"] = True
	ctx["html"] = s.get_text()

	return ctx


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
	success_url="/polity/%(polity)d/topic/%(id)d/"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		self.topic = get_object_or_404(Topic, id=kwargs["topic"])
		self.success_url = "/polity/" + str(self.polity.id) + "/topic/" + str(self.topic.id) + "/issue/%(id)d/"
		return super(IssueCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(IssueCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.topic.polity, 'topic': self.topic})
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
			self.membershiprequest, self.requested_membership = MembershipRequest.objects.get_or_create(polity=self.object, requestor=self.request.user)
			invite_count = MembershipVote.objects.filter(user=self.request.user, polity=self.object).count()
			invite_threshold = self.object.invite_threshold

			if self.object.members.count() < invite_threshold:
				invite_threshold = self.object.members.count()

			threshold_met = invite_threshold <= invite_count

			if threshold_met:
				self.object.members.add(self.request.user)
		else:
			try:
				self.membershiprequest = MembershipRequest.objects.get(polity=self.object, requestor=self.request.user)
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

		context_data.update(ctx)
		return context_data


class PolityCreateView(CreateView):
	model = Polity
	context_object_name = "polity"
	template_name = "core/polity_form.html"
	form_class = PolityForm
	success_url="/polity/%(id)d/"



class DocumentCreateView(CreateView):
	model = Document
	context_object_name = "document"
	template_name = "core/document_form.html"
	form_class = DocumentForm
	success_url="/polity/%(polity)d/document/%(id)d/"


	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		self.success_url = "/polity/" + str(self.polity.id) + "/document/$(id)d/"
		return super(DocumentCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(DocumentCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity})
		return context_data

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.polity = self.polity
		self.object.user = self.request.user
		self.object.save()
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

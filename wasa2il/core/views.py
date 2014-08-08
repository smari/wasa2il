
from datetime import datetime, timedelta
import decimal

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.template import RequestContext
from django.db import DatabaseError
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils import simplejson

# BEGIN - Imported from the original login functionality (could probably use cleaning up)
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.sites.models import get_current_site
from django.template.response import TemplateResponse
import urlparse
# END

from django.contrib.auth.models import User
from core.models import Candidate, Polity, Document, DocumentContent, Topic, Issue, Election, ElectionVote, UserProfile
from core.forms import DocumentForm, UserProfileForm, TopicForm, IssueForm, CommentForm, PolityForm, ElectionForm
from core.saml import authenticate, SamlException
from gateway.icepirate import configure_external_member_db
from hashlib import sha1

import schulze


def home(request):
    ctx = {}
    if request.user.is_authenticated():
        if settings.FRONT_POLITY:
            return HttpResponseRedirect("/")

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
    ctx = {
        'language_code': settings.LANGUAGE_CODE
    }
    return render_to_response("help/%s/%s.html" % (settings.LANGUAGE_CODE, page), ctx)


def profile(request, username=None):
    ctx = {}
    if username:
        subject = get_object_or_404(User, username=username)
    else:
        subject = request.user

    ctx["subject"] = subject
    ctx["profile"] = subject.get_profile()
    if subject == request.user:
        ctx["polities"] = subject.polity_set.all()
        for polity in ctx["polities"]:
            polity.readable = True
    else:
        ctx["polities"] = [p for p in subject.polity_set.all() if p.is_member(request.user) or p.is_listed]
        for polity in ctx["polities"]:
            if polity.is_nonmembers_readable or polity.is_member(request.user):
                polity.readable = True
            else:
                polity.readable = False

    # Get documents and documentcontents which user has made
    documentdata = []
    contents = subject.documentcontent_set.select_related('document').order_by('document__name', 'order')
    last_doc_id = 0
    for c in contents:
        if c.document_id != last_doc_id:
            documentdata.append(c.document) # Template will detect the type as Document and show as heading
            last_doc_id = c.document_id

        documentdata.append(c)

    ctx['documentdata'] = documentdata

    return render_to_response("profile.html", ctx, context_instance=RequestContext(request))


@login_required
def view_settings(request):
    ctx = {}
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.get_profile())
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()

            if 'picture' in request.FILES:
                f = request.FILES.get("picture")
                m = sha1()
                m.update(request.user.username)
                hash = m.hexdigest()
                ext = f.name.split(".")[1]
                filename = "userimg_%s.%s" % (hash, ext)
                path = settings.MEDIA_ROOT + "/" + filename
                #url = settings.MEDIA_URL + filename
                pic = open(path, 'wb+')
                for chunk in f.chunks():
                    pic.write(chunk)
                pic.close()
                p = request.user.get_profile()
                p.picture.name = filename
                p.save()

            return HttpResponseRedirect("/accounts/profile/")
        else:
            print "FAIL!"
            ctx["form"] = form
            return render_to_response("settings.html", ctx, context_instance=RequestContext(request))

    else:
        form = UserProfileForm(initial={'email': request.user.email}, instance=request.user.get_profile())

    ctx["form"] = form
    return render_to_response("settings.html", ctx, context_instance=RequestContext(request))


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            # Make sure that profile exists
            try:
                request.user.get_profile()
            except:
                profile = UserProfile()
                profile.user = request.user
                profile.save()

            if hasattr(settings, 'ICEPIRATE'): # Is IcePirate support enabled?
                if request.user.get_profile().verified_ssn:
                    configure_external_member_db(request.user, create_if_missing=False)
                else:
                    return HttpResponseRedirect(settings.AUTH_URL)

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@login_required
def verify(request):

    try:
        auth = authenticate(request, settings.AUTH_URL)
    except SamlException as e:
        ctx = {'e': e}
        return render_to_response('registration/saml_error.html', ctx)

    if UserProfile.objects.filter(verified_ssn=auth['ssn']).count() > 0:
        taken_user = UserProfile.objects.select_related('user').get(verified_ssn=auth['ssn']).user
        ctx = {
            'auth': auth,
            'taken_user': taken_user,
        }

        auth_logout(request)

        return render_to_response('registration/verification_duplicate.html', ctx)

    profile = request.user.get_profile() # It shall exist at this point
    profile.verified_ssn = auth['ssn']
    profile.verified_name = auth['name'].encode('utf8')
    profile.verified_token = request.GET['token']
    profile.verified_timing = datetime.now()
    profile.save()

    configure_external_member_db(request.user, create_if_missing=True)

    return HttpResponseRedirect('/')


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
    success_url = "/polity/%(polity)d/topic/%(id)d/"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        self.success_url = "/polity/" + str(self.polity.id) + "/topic/%(id)d/"
        return super(TopicCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(TopicCreateView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data['user_is_member'] = self.request.user in self.polity.members.all()
        return context_data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.polity = self.polity
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class TopicDetailView(DetailView):
    model = Topic
    context_object_name = "topic"
    template_name = "core/topic_detail.html"

    def get_context_data(self, *args, **kwargs):
        context_data = super(TopicDetailView, self).get_context_data(*args, **kwargs)
        context_data["delegation"] = self.object.get_delegation(self.request.user)
        context_data["polity"] = self.object.polity
        context_data['user_is_member'] = self.request.user in self.object.polity.members.all()
        return context_data


class IssueCreateView(CreateView):
    context_object_name = "issue"
    template_name = "core/issue_form.html"
    form_class = IssueForm
    success_url = "/issue/%(id)d/"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])

        if self.polity.is_newissue_only_officers and self.request.user not in self.polity.officers.all():
            raise PermissionDenied()

        return super(IssueCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(IssueCreateView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data['user_is_member'] = self.request.user in self.polity.members.all()
        context_data['form'].fields['topics'].queryset = Topic.objects.filter(polity=self.polity)
        context_data['selected_topics'] = []

        selected_topics = []
        if self.kwargs['documentcontent']:
            current_content = DocumentContent.objects.get(id=self.kwargs['documentcontent'])

            if current_content.order > 1:
                previous_topics = current_content.previous_topics()
                context_data['selected_topics'] = simplejson.dumps(previous_topics)
                context_data['tab'] = 'diff'
 
            context_data['documentcontent'] = current_content
            context_data['documentcontent_comments'] = current_content.comments.replace("\n", "\\n")
            context_data['selected_diff_documentcontent'] = current_content.document.preferred_version()

        return context_data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.polity = self.polity

        self.object.apply_ruleset()

        context_data = self.get_context_data(form=form)
        if 'documentcontent' in context_data:
            self.object.documentcontent = context_data['documentcontent']

        self.object.save()

        for topic in form.cleaned_data.get('topics'):
            self.object.topics.add(topic)

        return HttpResponseRedirect(self.get_success_url())


class IssueDetailView(DetailView):
    model = Issue
    context_object_name = "issue"
    template_name = "core/issue_detail.html"

    def get_context_data(self, *args, **kwargs):
        context_data = super(IssueDetailView, self).get_context_data(*args, **kwargs)

        documentcontent = self.object.documentcontent
        if documentcontent.order > 1:
            context_data['tab'] = 'diff'
        else:
            context_data['tab'] = 'view'

        context_data['documentcontent'] = documentcontent
        if self.object.is_processed:
            context_data['selected_diff_documentcontent'] = documentcontent.predecessor
        else:
            context_data['selected_diff_documentcontent'] = documentcontent.document.preferred_version()

        # TODO: Unused, as of yet.
        #context_data["delegation"] = self.object.get_delegation(self.request.user)

        votes_percentage_reached = 0
        votes = self.object.get_votes()
        if votes['count']:
            votes_percentage_reached = float(votes['yes']) / float(votes['count']) * 100

        context_data['votes_yes'] = votes['yes']
        context_data['votes_no'] = votes['no']
        context_data['votes_count'] = votes['count']
        context_data['votes_percentage_reached'] = votes_percentage_reached

        return context_data


class PolityDetailView(DetailView):
    model = Polity
    context_object_name = "polity"
    template_name = "core/polity_detail.html"

    def dispatch(self, *args, **kwargs):
        res = super(PolityDetailView, self).dispatch(*args, **kwargs)

        return res

    def get_context_data(self, *args, **kwargs):
        ctx = {}
        context_data = super(PolityDetailView, self).get_context_data(*args, **kwargs)

        ctx['user_is_member'] = self.request.user in self.object.members.all()
        ctx["politytopics"] = self.object.get_topic_list(self.request.user)
        ctx["delegation"] = self.object.get_delegation(self.request.user)
        ctx["newissues"] = self.object.issue_set.order_by("deadline_votes").filter(deadline_votes__gt=datetime.now())[:15]
        ctx["newelections"] = self.object.election_set.filter(deadline_votes__gt=datetime.now())[:10]
        ctx["settings"] = settings
        # ctx["delegations"] = Delegate.objects.filter(user=self.request.user, polity=self.object)

        context_data.update(ctx)
        return context_data


class PolityCreateView(CreateView):
    model = Polity
    context_object_name = "polity"
    template_name = "core/polity_form.html"
    form_class = PolityForm
    success_url = "/polity/%(id)d/"

    def form_valid(self, form):
        self.object = form.save()
        self.object.members.add(self.request.user)
        return super(PolityCreateView, self).form_valid(form)


class DocumentCreateView(CreateView):
    model = Document
    context_object_name = "document"
    template_name = "core/document_form.html"
    form_class = DocumentForm

    def dispatch(self, *args, **kwargs):
        self.polity = None
        if kwargs.has_key('polity'):
            try:
                self.polity = Polity.objects.get(id=kwargs["polity"])
            except Polity.DoesNotExist:
                pass # self.polity defaulted to None already.

        return super(DocumentCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(DocumentCreateView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data['user_is_member'] = self.request.user in self.polity.members.all()
        return context_data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.polity = self.polity
        self.object.user = self.request.user
        self.object.save()
        self.success_url = "/polity/" + str(self.polity.id) + "/document/" + str(self.object.id) + "/?v=new"
        return HttpResponseRedirect(self.get_success_url())


class DocumentDetailView(DetailView):
    model = Document
    context_object_name = "document"
    template_name = "core/document_update.html"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        return super(DocumentDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        doc = self.object

        context_data = super(DocumentDetailView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})

        if 'v' in self.request.GET:
            if self.request.GET['v'] == 'new':
                context_data['editor_enabled'] = True

                current_content = DocumentContent()
                current_content.order = 0

                inherited_content = self.object.preferred_version()

                if inherited_content:
                    current_content.text = inherited_content.text

            else:
                try:
                    current_content = get_object_or_404(DocumentContent, document=doc, order=int(self.request.GET['v']))
                except ValueError:
                    raise Exception('Bad "v(ersion)" parameter')
        else:
            current_content = self.object.preferred_version()


        try:
            issue = current_content.issue
        except Issue.DoesNotExist:
            issue = None


        user_is_member = self.request.user in self.polity.members.all()
        user_is_officer = self.request.user in self.polity.officers.all()

        buttons = {
            'propose_change': False,
            'put_to_vote': False,
        }
        if not issue or not issue.is_voting():
            if current_content.status == 'accepted':
                if user_is_member:
                    buttons['propose_change'] = 'enabled'
            elif current_content.status == 'proposed':
                if user_is_officer and not issue:
                    buttons['put_to_vote'] = 'disabled' if doc.has_open_issue() else 'enabled'

        context_data['current_content'] = current_content
        context_data['selected_diff_documentcontent'] = doc.preferred_version
        context_data['issue'] = issue
        context_data['buttons'] = buttons

        context_data.update(csrf(self.request))
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
        context_data['user_is_member'] = self.request.user in self.polity.members.all()
        return context_data


class ElectionCreateView(CreateView):
    model = Election
    context_object_name = "election"
    template_name = "core/election_form.html"
    form_class = ElectionForm
    success_url = "/polity/%(polity)d/election/%(id)d/"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        self.success_url = "/polity/" + str(self.polity.id) + "/election/$(id)d/"
        return super(ElectionCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(ElectionCreateView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data['user_is_member'] = self.request.user in self.polity.members.all()
        return context_data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.polity = self.polity
        self.object.save()
        self.success_url = "/polity/" + str(self.polity.id) + "/election/" + str(self.object.id) + "/"
        return HttpResponseRedirect(self.get_success_url())


class ElectionDetailView(DetailView):
    model = Election
    context_object_name = "election"
    template_name = "core/election_detail.html"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        return super(ElectionDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):

        # Single variable for template to check which controls to enable
        voting_interface_enabled = self.get_object().polity.is_member(self.request.user) and self.get_object().is_voting

        if self.get_object().deadline_joined_org:
            votes = ElectionVote.objects.select_related('candidate__user').filter(election=self.get_object(), user__userprofile__joined_org__lt = self.get_object().deadline_joined_org)
        else:
            votes = ElectionVote.objects.select_related('candidate__user').filter(election=self.get_object())
        candidates = Candidate.objects.select_related('user').filter(election=self.get_object())
        votemap = {}
        for vote in votes:
            if not votemap.has_key(vote.user_id):
                votemap[vote.user_id] = []

            votemap[vote.user_id].append(vote)

        manger = []
        for user_id in votemap:
            manger.append([(v.value, v.candidate) for v in votemap[user_id]])

        preference = schulze.rank_votes(manger, candidates)
        strongest_paths = schulze.compute_strongest_paths(preference, candidates)

        election_results = schulze.get_ordered_voting_results(strongest_paths)

        context_data = super(ElectionDetailView, self).get_context_data(*args, **kwargs)
        context_data.update(
            {
                'polity': self.polity,
                "now": datetime.now().strftime("%d/%m/%Y %H:%I"),
                'election_results': election_results,
                'voting_interface_enabled': voting_interface_enabled,
            }
        )
        return context_data


class ElectionListView(ListView):
    model = Election
    context_object_name = "elections"
    template_name = "core/election_list.html"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        return super(ElectionListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(ElectionListView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data['user_is_member'] = self.request.user in self.polity.members.all()
        return context_data


def election_ballots(request, pk=None):
    ctx = {}
    election = get_object_or_404(Election, pk=pk)
    if election.is_closed():
        ctx["ballotbox"] = election.get_ballots()
        return render_to_response("core/election_ballots.txt", ctx, mimetype="text/plain", context_instance=RequestContext(request))
    else:
        raise PermissionDenied


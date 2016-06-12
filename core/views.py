
from datetime import datetime, timedelta
import os.path
import decimal
import json

# for Discourse SSO support
import base64
import hmac
import hashlib
import urllib
from urlparse import parse_qs
# SSO done

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import Http404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.template import RequestContext
from django.db import DatabaseError
from django.db.models import Q
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils.translation import ugettext as _

# BEGIN - Copied from django.contrib.auth.views to accommodate the login() function
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
# END

from django.contrib.auth.models import User
from core.models import Candidate, Polity, Document, DocumentContent, Topic, Issue, Election, ElectionVote, UserProfile
from core.forms import DocumentForm, UserProfileForm, TopicForm, IssueForm, CommentForm, PolityForm, ElectionForm
from core.saml import authenticate, SamlException
from gateway.icepirate import configure_external_member_db
from hashlib import sha1


def home(request):
    ctx = {}

    try:
        polity = Polity.objects.get(is_front_polity=True)
        return HttpResponseRedirect("/polity/%d/" % polity.id)
    except Polity.DoesNotExist:
        pass

    if request.user.is_authenticated():
        if request.user.is_staff and Polity.objects.count() == 0:
            return HttpResponseRedirect("/polity/new")

        return HttpResponseRedirect("/accounts/profile/")
    else:
        return render_to_response("entry.html", ctx, context_instance=RequestContext(request))


def help(request, page):
    ctx = {
        'language_code': settings.LANGUAGE_CODE
    }
    for locale in [settings.LANGUAGE_CODE, "is"]: # Icelandic fallback
      filename = "help/%s/%s.html" % (locale, page)
      if os.path.isfile(os.path.join(os.path.dirname(__file__), '..', 'wasa2il/templates', filename)):
          return render_to_response(filename, ctx, context_instance=RequestContext(request))

    raise Http404


def profile(request, username=None):
    ctx = {}
    if username:
        subject = get_object_or_404(User, username=username)
    elif request.user.is_authenticated():
        subject = request.user
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)

    ctx["subject"] = subject
    ctx["profile"] = UserProfile.objects.get(user=subject)
    if subject == request.user:
        ctx["polities"] = subject.polity_set.all()
    else:
        ctx["polities"] = [p for p in subject.polity_set.all() if p.is_member(request.user) or p.is_listed]

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
        form = UserProfileForm(request.POST, request=request, instance=UserProfile.objects.get(user=request.user))
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()

            if 'picture' in request.FILES:
                f = request.FILES.get("picture")
                m = sha1()
                m.update(request.user.username)
                hash = m.hexdigest()
                ext = f.name.split(".")[1] # UserProfileForm.clean_picture() makes sure this is safe.
                filename = "userimg_%s.%s" % (hash, ext)
                path = settings.MEDIA_ROOT + "/" + filename
                #url = settings.MEDIA_URL + filename
                pic = open(path, 'wb+')
                for chunk in f.chunks():
                    pic.write(chunk)
                pic.close()
                p = request.user.userprofile
                p.picture.name = filename
                p.save()

            return HttpResponseRedirect("/accounts/profile/")
        else:
            print "FAIL!"
            ctx["form"] = form
            return render_to_response("settings.html", ctx, context_instance=RequestContext(request))

    else:
        form = UserProfileForm(initial={'email': request.user.email}, instance=UserProfile.objects.get(user=request.user))

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
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            # Make sure that profile exists
            try:
                UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                profile = UserProfile()
                profile.user = request.user
                profile.save()

            if hasattr(settings, 'SAML_1'): # Is SAML 1.2 support enabled?
                if not request.user.userprofile.verified_ssn:
                    return HttpResponseRedirect(settings.SAML_1['URL'])

            if hasattr(settings, 'ICEPIRATE'): # Is IcePirate support enabled?
                configure_external_member_db(request.user, create_if_missing=False)

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

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
        auth = authenticate(request, settings.SAML_1['URL'])
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

    profile = request.user.userprofile # It shall exist at this point
    profile.verified_ssn = auth['ssn']
    profile.verified_name = auth['name'].encode('utf8')
    profile.verified_token = request.GET['token']
    profile.verified_timing = datetime.now()
    profile.save()

    if hasattr(settings, 'ICEPIRATE'): # Is IcePirate support enabled?
        configure_external_member_db(request.user, create_if_missing=True)

    return HttpResponseRedirect('/')

@login_required
def sso(request):
    if not hasattr(settings, 'DISCOURSE'):
        raise Http404

    key = str(settings.DISCOURSE['secret'])
    return_url = '%s/session/sso_login' % settings.DISCOURSE['url']

    payload = request.GET.get('sso')
    their_signature = request.GET.get('sig')

    if None in [payload, their_signature]:
        return HttpResponseBadRequest('Required parameters missing.')

    try:
        payload = urllib.unquote(payload)
        decoded = base64.decodestring(payload)
        assert 'nonce' in decoded
        assert len(payload) > 0
    except:
        return HttpResponseBadRequest('Malformed payload.')

    our_signature = hmac.new(key, payload, digestmod=hashlib.sha256).hexdigest()

    if our_signature != their_signature:
        return HttpResponseBadRequest('Malformed payload.')

    nonce = parse_qs(decoded)['nonce'][0]
    outbound = {
        'nonce': nonce,
        'email': request.user.email,
        'external_id': request.user.id,
        'username': request.user.username,
    }

    out_payload = base64.encodestring(urllib.urlencode(outbound))
    out_signature = hmac.new(key, out_payload, digestmod=hashlib.sha256).hexdigest()
    out_query = urllib.urlencode({'sso': out_payload, 'sig' : out_signature})

    return HttpResponseRedirect('%s?%s' % (return_url, out_query))

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
                context_data['selected_topics'] = json.dumps(previous_topics)
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

        if self.object.documentcontent:
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
        context_data['facebook_title'] = '%s, %s (%s)' % (self.object.name, _(u'voting'), self.object.polity.name)

        return context_data


class IssueOpenListView(ListView):
    model = Issue
    context_object_name = 'newissues'
    template_name = "core/issues_new.html"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs['polity'])
        return super(IssueOpenListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return self.polity.issue_set.order_by('deadline_votes').filter(deadline_votes__gt=datetime.now())

    def get_context_data(self, *args, **kwargs):
        context_data = super(IssueOpenListView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
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
        self.object.update_agreements()
        ctx['user_is_member'] = self.request.user in self.object.members.all()
        ctx["politytopics"] = self.object.get_topic_list(self.request.user)
        ctx["delegation"] = self.object.get_delegation(self.request.user)
        ctx["newissues"] = self.object.issue_set.order_by("deadline_votes").filter(deadline_votes__gt=datetime.now())[:20]
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
        self.success_url = "/polity/" + str(self.polity.id) + "/document/" + str(self.object.id) + "/?action=new"
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

        # Request variables taken together
        action = self.request.GET.get('action', '')
        try:
            version_num = int(self.request.GET.get('v', 0))
        except ValueError:
            raise Exception('Bad "v(ersion)" parameter')

        # If version_num is not specified, we want the "preferred" version
        if version_num > 0:
            current_content = get_object_or_404(DocumentContent, document=doc, order=version_num)
        else:
            current_content = doc.preferred_version()


        issue = None
        if current_content is not None and hasattr(current_content, 'issue'):
            issue = current_content.issue


        if action == 'new':
            context_data['editor_enabled'] = True

            current_content = DocumentContent()
            current_content.order = 0
            current_content.predecessor = doc.preferred_version()

            if current_content.predecessor:
                current_content.text = current_content.predecessor.text

        elif action == 'edit':
            if current_content.user.id == self.request.user.id and current_content.status == 'proposed' and issue is None:
                context_data['editor_enabled'] = True


        user_is_member = self.request.user in self.polity.members.all()
        user_is_officer = self.request.user in self.polity.officers.all()

        buttons = {
            'propose_change': False,
            'put_to_vote': False,
            'edit_proposal': False,
        }
        if not issue or not issue.is_voting():
            if current_content.status == 'accepted':
                if user_is_member:
                    buttons['propose_change'] = 'enabled'
            elif current_content.status == 'proposed':
                if user_is_officer and not issue:
                    buttons['put_to_vote'] = 'disabled' if doc.has_open_issue() else 'enabled'
                if current_content.user_id == self.request.user.id:
                    buttons['edit_proposal'] = 'disabled' if issue is not None else 'enabled'

        context_data['action'] = action
        context_data['current_content'] = current_content
        context_data['selected_diff_documentcontent'] = doc.preferred_version
        context_data['issue'] = issue
        context_data['buttons'] = buttons
        context_data['facebook_title'] = '%s (%s)' % (self.object.name, self.object.polity.name)

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
        context_data.update({'agreements': [x.preferred_version() for x in context_data["documents"]]})
        context_data['user_is_member'] = self.request.user in self.polity.members.all()
        return context_data

class SearchListView(ListView):
    model = Document
    context_object_name = "documents"
    template_name = "search.html"

    def dispatch(self, *args, **kwargs):
        return super(SearchListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(SearchListView, self).get_context_data(*args, **kwargs)
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

        if self.get_object().is_processed:
            election_result = self.get_object().result
            ordered_candidates = [r.candidate for r in election_result.rows.order_by('order')]
            vote_count = election_result.vote_count
        else:
            # FIXME: This will be horribly, horribly slow for some voting systems. Also,
            #        revealing the current status of an ongoing election is probably very
            #        much the wrong thing to do!
            ordered_candidates = self.get_object().get_ordered_candidates_from_votes()
            vote_count = self.get_object().get_vote_count

        context_data = super(ElectionDetailView, self).get_context_data(*args, **kwargs)
        context_data.update(
            {
                'polity': self.polity,
                "now": datetime.now().strftime("%d/%m/%Y %H:%I"),
                'ordered_candidates': ordered_candidates,
                'vote_count': vote_count,
                'voting_interface_enabled': voting_interface_enabled,
                'user_is_member': self.request.user in self.polity.members.all(),
                'facebook_title': '%s (%s)' % (self.get_object().name, self.polity.name),
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

        elections = Election.objects.filter(polity=self.polity).annotate(candidate_count=Count('candidate')).order_by('-deadline_votes')

        context_data = super(ElectionListView, self).get_context_data(*args, **kwargs)
        context_data.update({
            'polity': self.polity,
            'elections': elections,
        })

        return context_data


def election_ballots(request, pk=None):
    ctx = {}
    election = get_object_or_404(Election, pk=pk)
    if election.is_closed():
        ctx["ballotbox"] = election.get_ballots()
        return render_to_response("core/election_ballots.txt", ctx, context_instance=RequestContext(request), content_type="text/plain")
    else:
        raise PermissionDenied


def error500(request):
    return render_to_response('500.html')


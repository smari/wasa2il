
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from core.models import Document, Issue, ChangeProposal, Statement, DocumentContent
from core.json.utils import jsonize


@login_required
@jsonize
def document_propose_change(request):
	ctx = {"ok": True}
	document = get_object_or_404(Document, id=request.POST.get("document_id", 0))

	try:
		text = request.POST['text']
	except KeyError:
		raise Exception('Missing "text"')
	try:
		diff = request.POST['diff']
	except KeyError:
		raise Exception('Missing "diff"')
	try:
		patch = request.POST['patch']
	except KeyError:
		raise Exception('Missing "patch"')

	content = DocumentContent()
	content.document = document
	content.user = request.user
	content.comments = request.POST.get('comments', '')
	content.text = text
	content.diff = diff
	content.patch = patch
	try:
		content.order = DocumentContent.objects.filter(document=document).order_by('-order')[0].order + 1
	except IndexError:
		pass
	content.save()

	ctx['order'] = content.order

	return ctx


@login_required
@jsonize
def issue_document_import(request):
	ctx = {"ok": True}

	issue = get_object_or_404(Issue, id=request.REQUEST.get("issue"))
	doc = get_object_or_404(Document, id=request.REQUEST.get("document"))

	if not doc.polity == issue.polity:
		return {"ok": False}

	if not doc.is_adopted:
		return {"ok": False}

	doc.issues.add(issue)

	return ctx


@login_required
@jsonize
def document_changeproposal_new(request, document, type):
	ctx = {}

	doc = get_object_or_404(Document, id=document)

	if request.user not in doc.polity.members.all():
		ctx['error'] = 403
		return ctx

	s = ChangeProposal()
	s.user = request.user
	s.document = doc
	s.contenttype = type
	s.actiontype = 4
	s.refitem = request.GET.get('after')
	s.destination = request.GET.get('after')  # TODO: Not correct...
	s.content = request.GET.get('text', '')
	s.save()

	return ctx


@login_required
@jsonize
def document_statements_import(request):
	ctx = {}
	ctx["list"] = []

	doc = get_object_or_404(Document, id=request.GET.get("document"))
	text = request.GET.get("text", "")
	lines = text.split("\n")

	if request.user != doc.user:
		return {"error": 403}

	for line in lines:
		s = Statement()
		s.user = request.user
		s.document = doc
		s.text = line[1:].strip()

		if len(line) == 0:
			continue

		if line[0] == "\#":
			# Subheading
			s.type = 3
		elif line[0] == "-":
			# Reference
			s.type = 0
		elif line[0] == ":":
			# Assumption
			s.type = 1
		elif line[0] == "*":
			# Statement
			s.type = 2
		else:
			continue

		try:
			s.number = Statement.objects.get(document=s.document, type=s.type).order_by('-number')[0].number + 1
		except:
			s.number = 1

		s.save()

		boom = {}
		boom["id"] = s.id
		boom["seq"] = s.number
		boom["html"] = str(s)
		ctx["list"].append(boom)

	return ctx


@login_required
@jsonize
def document_statement_new(request, document, type):
	ctx = {}

	doc = get_object_or_404(Document, id=document)

	if doc.is_proposed:
		return document_changeproposal_new(request, document, type)

	s = Statement()
	s.user = request.user
	s.document = doc
	s.type = type
	s.text = request.GET.get('text', '')

	if s.user != s.document.user:
		return {"error": 403}

	try:
		s.number = Statement.objects.get(document=s.document, type=s.type).order_by('-number')[0].number + 1
	except:
		s.number = 1

	s.save()

	ctx["ok"] = True
	ctx["id"] = s.id
	ctx["seq"] = s.number
	ctx["html"] = str(s)

	return ctx


@login_required
@jsonize
def document_statement_move(request, statement, order):
	return {}


@login_required
@jsonize
def document_statement_delete(request, statement):
	return {}


@login_required
@jsonize
def document_propose(request, document, state):
	ctx = {}

	document = get_object_or_404(Document, id=document)

	if request.user != document.user:
		return {"error": 403}

	ctx["state"] = bool(int(state))
	document.is_proposed = bool(int(state))
	document.save()

	issue_id = int(request.REQUEST.get("issue", 0))
	if issue_id:
		issue = Issue.objects.get(id=issue_id)
		ctx["html_user_documents"] = render_to_string("core/_document_proposals_list_table.html", {"documents": issue.user_documents(request.user)})
		ctx["html_all_documents"] = render_to_string("core/_document_list_table.html", {"documents": issue.proposed_documents()})

	ctx["ok"] = True
	return ctx

from django.shortcuts import render_to_response

def home(request):
	ctx = {}

	return render_to_response("home.html", ctx)

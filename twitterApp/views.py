from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.

# def index(request):
# 	return render(request, 'twitterApp/index.html', {})

class IndexView(TemplateView):
    template_name = "twitterApp/index.html"

class SignedInView(TemplateView):
	template_name = "twitterApp/signedIn.html"

class EmailSubmittedView(TemplateView):
	template_name = "twitterApp/emailSubmitted.html"

def signIn(request):
	return HttpResponseRedirect(reverse('twitterApp:signedIn'))

def submitEmail(request):
	return HttpResponseRedirect(reverse('twitterApp:emailSubmitted'))




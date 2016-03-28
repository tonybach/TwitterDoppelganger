from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import requests
import json
import utils
import calculations

# def index(request):
# 	return render(request, 'twitterApp/index.html', {})

class IndexView(TemplateView):
    template_name = "twitterApp/index.html"


class SignedInView(TemplateView):
	template_name = "twitterApp/signedIn.html"


class EmailSubmittedView(TemplateView):
	template_name = "twitterApp/emailSubmitted.html"


def signIn(request):
	response = utils.sign_in()
	oauth_token = response.text[12:response.text.find('&oauth_token_secret')]
	redirect_url = "https://api.twitter.com/oauth/authenticate?oauth_token=" + oauth_token

	return HttpResponseRedirect(redirect_url)


def submitEmail(request):
	twitter_params = request.POST["twitter_params"]
	oauth_token= twitter_params[twitter_params.find("oauth_token")+12:twitter_params.find("&oauth_verifier")]
	oauth_verifier = twitter_params[twitter_params.find("oauth_verifier")+15:]

	response, consumer_key, consumer_secret = utils.convert_to_access_token(oauth_token, oauth_verifier)
	r = response.text
	access_token = r[12:r.find("&oauth_token_secret")]
	access_token_secret = r[r.find("&oauth_token_secret")+20:r.find("&user_id")]
	user_id = r[r.find("&user_id")+9:r.find("&screen_name")]
	screen_name = r[r.find("&screen_name")+13:r.find("&x_auth")]

	calculations.find_similarities(consumer_key, consumer_secret, access_token, access_token_secret, screen_name)
	return HttpResponseRedirect(reverse('twitterApp:emailSubmitted'))




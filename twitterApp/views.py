from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import requests
import json
import time
from hashlib import sha1
import hmac
import base64
import random
import urllib
import utils

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
	# utils.signIn()
	url = "https://api.twitter.com/oauth/request_token"
	# url = "https://api.twitter.com/1/statuses/update.json"
	oauth_callback = "http://localhost:8000/signedIn"

	oauth_consumer_key = "Zj2eZw7kpCCocZz0STOG21xvD"
	# oauth_consumer_key = "xvz1evFS4wEEPTGEFPHBog"
	# oauth_nonce = base64.b64encode(''.join([str(random.randint(0, 9)) for i in range(24)]))
	oauth_nonce = "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg"
	oauth_signature_method = "HMAC-SHA1"
	oauth_timestamp = str(int(time.time()))
	# oauth_timestamp = "1318622958"
	oauth_token = "294030079-VMDhU95SZq9iy18HSWE91tzrM2Pnn8FeL41Qu6Tc"
	# oauth_token = "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb"
	oauth_version = "1.0"

	# parameter_string="include_entities=true&oauth_consumer_key=%s&oauth_nonce=%s&oauth_signature_method=%s&oauth_timestamp=%s&oauth_token=%s&oauth_version=%s&status=Hello%%20Ladies%%20%%2B%%20Gentlemen%%2C%%20a%%20signed%%20OAuth%%20request%%21" %(oauth_consumer_key, oauth_nonce, oauth_signature_method, oauth_timestamp, oauth_token, oauth_version)
	parameter_string="oauth_consumer_key=%s&oauth_nonce=%s&oauth_signature_method=%s&oauth_timestamp=%s&oauth_token=%s&oauth_version=%s" %(oauth_consumer_key, oauth_nonce, oauth_signature_method, oauth_timestamp, oauth_token, oauth_version)
	signature_base_string = "POST&" + urllib.quote_plus(url) + "&" + urllib.quote_plus(parameter_string)

	consumer_secret = "R6GjEMJhNpi0oSct9QLdi7tLnNMBniyCqPkTMuklgVjfMQftTo"
	# consumer_secret = "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw"
	oauth_token_secret = "46Bj3WENOaUpfNYIzDcTyExIY6xXxAppMD6VeMQidfhVN"
	# oauth_token_secret = "LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE"
	signing_key = urllib.quote_plus(consumer_secret) + "&" + urllib.quote_plus(oauth_token_secret)

	hashed = hmac.new(signing_key, signature_base_string, sha1)
	oauth_signature = hashed.digest().encode("base64").rstrip('\n')

	headers = {"Authorization":
				'OAuth oauth_callback="%s", '%(urllib.quote_plus(oauth_callback))+
				'oauth_consumer_key="%s", '%(oauth_consumer_key) +
				'oauth_nonce="%s", '%(oauth_nonce) +
				'oauth_signature="%s", '%(urllib.quote_plus(oauth_signature)) +
				'oauth_signature_method="%s", '%(oauth_signature_method) + 
				'oauth_timestamp="%s", '%(oauth_timestamp) + 
				# 'oauth_token="%s", '%(oauth_token) +
				'oauth_version="%s"'%(oauth_version)
			}

	# r = requests.post(url, headers=headers)
	r = utils.signIn()
	response = r.text
	end_index = response.find('&oauth_token_secret')
	token = response[12:end_index]
	# return HttpResponse(headers["Content-Type"])
	print response
	# return HttpResponse(token)
	# return HttpResponse(oauth_signature)
	redirect_url = "https://api.twitter.com/oauth/authenticate?oauth_token=" + token
	return HttpResponseRedirect(redirect_url)

def submitEmail(request):
	twitter_params = request.POST["twitter_params"]
	oauth_verifier = twitter_params[twitter_params.find("oauth_verifier")+15:]
	r = utils.convertToAccessToken(oauth_verifier)
	print(r.text)
	return HttpResponseRedirect(reverse('twitterApp:emailSubmitted'))




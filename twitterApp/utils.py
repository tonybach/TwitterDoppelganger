import ConfigParser
import time
import collections
import base64
import random
import urllib
import hmac
import hashlib
import binascii
import requests

def convertToAccessToken(oauth_verifier):
	config = ConfigParser.RawConfigParser()
	config.read('twitterApp/settings.cfg')

	method = "post"
	url = "https://api.twitter.com/oauth/access_token"
	# callback_url = "http://localhost:8000/emailSubmitted"

	keys = {
		"twitter_consumer_secret": config.get('Keys', 'twitter_consumer_secret'),
		"twitter_consumer_key": config.get('Keys', 'twitter_consumer_key'),
		"access_token": config.get('Keys', 'access_token'),
		"access_token_secret": config.get('Keys', 'access_token_secret')
	}

	oauth_parameters = get_oauth_parameters(
		keys['twitter_consumer_key'],
		keys['access_token']
	)

	oauth_parameters['oauth_signature'] = generate_signature(
		method,
		url,
		oauth_parameters,
		keys['twitter_consumer_secret'],
		keys['access_token_secret'],
		oauth_verifier
	)

	headers = {"Host": "api.twitter.com", 'Authorization': create_auth_header(oauth_parameters)}
	r = requests.post(url, headers=headers)
	print r.text

	return r

def signIn():
	config = ConfigParser.RawConfigParser()
	config.read('twitterApp/settings.cfg')

	method = "post"
	url = "https://api.twitter.com/oauth/request_token"
	callback_url = "http://localhost:8000/signedIn"

	keys = {
		"twitter_consumer_secret": config.get('Keys', 'twitter_consumer_secret'),
		"twitter_consumer_key": config.get('Keys', 'twitter_consumer_key'),
		"access_token": config.get('Keys', 'access_token')
	}

	oauth_parameters = get_oauth_parameters(
		keys['twitter_consumer_key'],
		"",
		callback_url
	)

	oauth_parameters['oauth_signature'] = generate_signature(
		method,
		url,
		oauth_parameters,
		keys['twitter_consumer_secret']
		# keys['access_token_secret']
	)

	# headers = {"Host": "api.twitter.com", 'Authorization': create_auth_header(oauth_parameters)}
	headers = {"Host": "api.twitter.com", 'Authorization': create_auth_header(oauth_parameters)}
	r = requests.post(url, headers=headers)
	print r.text

	return r

def get_oauth_parameters(consumer_key, access_token, callback_url=None):
	oauth_parameters = {
		'oauth_timestamp': str(int(time.time())),
		'oauth_signature_method': "HMAC-SHA1",
		'oauth_version': "1.0",
		'oauth_token': access_token,
		'oauth_nonce': get_nonce(),
		'oauth_consumer_key': consumer_key
	}
	if (callback_url):
		oauth_parameters['oauth_callback'] = callback_url
	return oauth_parameters

def get_nonce():
	"""Unique token generated for each request"""
	n = base64.b64encode(
	    ''.join([str(random.randint(0, 9)) for i in range(24)]))
	return n

def generate_signature(method, url, oauth_parameters, twitter_consumer_secret, access_token_secret=None, request_body=None):
	temp = collect_parameters(oauth_parameters, request_body)
	parameter_string = stringify_parameters(temp)
	signature_base_string = method.upper() + '&' + escape(str(url)) + '&' + escape(parameter_string)
	print(signature_base_string)
	signing_key = create_signing_key(twitter_consumer_secret)
	return calculate_signature(signature_base_string, signing_key)


def collect_parameters(oauth_parameters, request_body):
    temp = oauth_parameters.copy()

    if request_body is not None:
        temp['oauth_verifier'] = request_body

    return temp

def stringify_parameters(parameters):
	output = ''
	ordered_paramaters = {}
	ordered_paramaters = collections.OrderedDict(sorted(parameters.items()))
	counter = 1

	for k, v in ordered_paramaters.iteritems():
		output += str(k) + '=' + str(v)
		if counter < len(ordered_paramaters):
			output += '&'
			counter += 1

	return output


def create_signing_key(oauth_consumer_secret, oauth_token_secret=None):
	signing_key = escape(oauth_consumer_secret) + '&'

	if oauth_token_secret is not None:
		signing_key += escape(oauth_token_secret)

	return signing_key


def calculate_signature(signature_base_string, signing_key):
	hashed = hmac.new(signing_key, signature_base_string, hashlib.sha1)
	# sig = binascii.b2a_base64(hashed.digest())[:-1]
	sig = hashed.digest().encode("base64").rstrip('\n')
	return escape(sig)


def create_auth_header(parameters):
# def create_auth_header(parameters, callback_url):
	ordered_paramaters = {}
	ordered_paramaters = collections.OrderedDict(sorted(parameters.items()))

	# oauth_callback = 'oauth_callback="%s", ' %(escape(callback_url))
	auth_header = ('%s="%s"' % (k, v) for k, v in ordered_paramaters.iteritems())
	val = "OAuth " + ', '.join(auth_header)
	# val = "OAuth " + oauth_callback + ', '.join(auth_header)
	return val

def escape(s):
	return urllib.quote_plus(s)

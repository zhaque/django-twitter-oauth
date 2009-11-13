import oauth, httplib, simplejson, urllib2
from django.conf import settings
from django.contrib.auth.models import User

signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

SERVER = getattr(settings, 'OAUTH_SERVER', 'twitter.com')
REQUEST_TOKEN_URL = getattr(settings, 'OAUTH_REQUEST_TOKEN_URL', 'https://%s/oauth/request_token' % SERVER)
ACCESS_TOKEN_URL = getattr(settings, 'OAUTH_ACCESS_TOKEN_URL', 'https://%s/oauth/access_token' % SERVER)
AUTHORIZATION_URL = getattr(settings, 'OAUTH_AUTHORIZATION_URL', 'http://%s/oauth/authorize' % SERVER)

CONSUMER_KEY = getattr(settings, 'CONSUMER_KEY', 'YOUR_KEY')
CONSUMER_SECRET = getattr(settings, 'CONSUMER_SECRET', 'YOUR_SECRET')

# We use this URL to check if Twitters oAuth worked
TWITTER_CHECK_AUTH = 'https://twitter.com/account/verify_credentials.json'
TWITTER_STATUS = 'https://twitter.com/statuses/update.json'
TWITTER_FRIENDS = 'https://twitter.com/statuses/friends.json'
TWITTER_USER_TIMELINE = 'https://twitter.com/statuses/user_timeline.json'

CONSUMER = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
CONNECTION = httplib.HTTPSConnection(SERVER)

def get_site_twitter_user():
	return get_or_create_twitter_user(settings.TWITTER_USERNAME)

def get_or_create_twitter_user(screen_name):
	try:
		return User.objects.get(username=screen_name)
	except User.DoesNotExist:
		u = User.objects.create_user(screen_name, '%s@twitter.com' % screen_name)
		u.save()
		return u

"""
class RequestWithMethod(urllib2.Request):
	def __init__(self, method, *args, **kwargs):
		self._method = method
		urllib2.Request.__init__(self, *args, **kwargs)

	def get_method(self):
		return self._method

def post(oauth_request, connection):
	url = oauth_request.get_normalized_http_url()
	data = oauth_request.to_postdata()
	
	req = RequestWithMethod('post', url, data)
	r = urllib2.urlopen(req)
	s = response.read()
	return r.status_code, s
"""

def request_oauth_resource(consumer, url, access_token, parameters=None, signature_method=signature_method, http_method='GET'):
	"""
	usage: request_oauth_resource( consumer, '/url/', your_access_token, parameters=dict() )
	Returns a OAuthRequest object
	"""
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, token=access_token, http_url=url, http_method=http_method, parameters=parameters,
	)
	oauth_request.sign_request(signature_method, consumer, access_token)
	return oauth_request
	
def fetch_response(oauth_request, connection):
	url = oauth_request.to_url()
	connection.request(oauth_request.http_method, url)
	response = connection.getresponse()
	s = response.read()
	return s
	

def post_and_fetch_response(oauth_request, connection):
	url = oauth_request.get_normalized_http_url()
	data = oauth_request.to_postdata()
	connection.request(oauth_request.http_method, url, data)
	r = connection.getresponse()
	s = r.read()
	return r.status, s

def get_unauthorised_request_token(consumer, connection, signature_method=signature_method):
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, http_url=REQUEST_TOKEN_URL
	)
	oauth_request.sign_request(signature_method, consumer, None)
	resp = fetch_response(oauth_request, connection)
	token = oauth.OAuthToken.from_string(resp)
	return token


def get_authorisation_url(consumer, token, signature_method=signature_method):
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, token=token, http_url=AUTHORIZATION_URL
	)
	oauth_request.sign_request(signature_method, consumer, token)
	return oauth_request.to_url()

def exchange_request_token_for_access_token(consumer, connection, request_token, signature_method=signature_method):
	oauth_request = oauth.OAuthRequest.from_consumer_and_token(
		consumer, token=request_token, http_url=ACCESS_TOKEN_URL
	)
	oauth_request.sign_request(signature_method, consumer, request_token)
	resp = fetch_response(oauth_request, connection)
	return oauth.OAuthToken.from_string(resp)
	
class Twitter(object):
	def is_authenticated(self):
		raise Exception('Not implemented')
		
	def get(self, url, data=None):
		raise Exception('Not implemented')
		
	def post(self, url, data=None):
		raise Exception('Not implemented')
	
	def set_status(self, text):
		return self.post(TWITTER_STATUS, {'status':text})
		
	def get_friends(self, page=0):
		return self.get(TWITTER_FRIENDS, {'page':page})
		
	def get_user_timeline(self, page=0):
		return self.get(TWITTER_USER_TIMELINE, {'page': page})
		

class TwitterClient(Twitter):
	def __init__(self, token):
		self.token = token
		self.consumer = CONSUMER
		self.connection = CONNECTION
		
	def post(self, url, data={}):
		oauth_request = request_oauth_resource(self.consumer, url, self.token, data, http_method='POST')
		r, json = post_and_fetch_response(oauth_request, self.connection)
		if r == 200:
			return simplejson.loads(json)
		else:
			raise Exception('Bad status code (%s): %s' % (r.status, json))
		
	def get(self, url, data={}):
		oauth_request = request_oauth_resource(self.consumer, url, self.token, data)
		json = fetch_response(oauth_request, self.connection)
		return simplejson.loads(json)
		
	def is_authenticated(self):
		oauth_request = request_oauth_resource(self.consumer, TWITTER_CHECK_AUTH, self.token)
		json = fetch_response(oauth_request, self.connection)
		if 'screen_name' in json:
			return simplejson.loads(json)
		return False

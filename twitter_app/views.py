import simplejson, time, datetime

from django.contrib.auth import login, get_backends
from django.http import *
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse

from twitter_app.utils import *
from twitter_app.decorators import oauth_required

def render_to(template=''):
	def deco(view):
		def fn(request, *args, **kargs):
			if 'template' in kargs:
				t = kargs['template']
				del kargs['template']
			else:
				t = template
			r = view(request, *args, **kargs) or {}
			if isinstance(r, HttpResponse):
				return r
			else:
				c = RequestContext(request, r)
				return render_to_response(t, context_instance=c)
		return fn
	return deco
	
def main(request):
	if request.session.has_key('access_token'):
		return HttpResponseRedirect(reverse('twitter_oauth_friend_list'))
	else:
		return render_to_response('twitter_app/base.html')


def auth(request):
	"/auth/"
	token = get_unauthorised_request_token(CONSUMER, CONNECTION)
	auth_url = get_authorisation_url(CONSUMER, token)
	response = HttpResponseRedirect(auth_url)
	request.session['unauthed_token'] = token.to_string()
	return response
	
def unauth(request):
	response = HttpResponseRedirect(reverse('twitter_oauth_main'))
	request.session.clear()
	return response
	
@oauth_required
def login_(request):
	auth = request.twitter.is_authenticated()
	if auth:
		user = get_or_create_twitter_user(auth['screen_name'])
		backend = get_backends()[0]
		user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
		login(request, user)
	next = request.session.get('next')
	if next:
		return HttpResponseRedirect(next)
	#return HttpResponseRedirect(reverse('twitter_oauth_main'))
	return HttpResponse('Logged in as Django User "%s" (%s)' % (user, request.session))

def return_(request):
	"/return/"
	unauthed_token = request.session.get('unauthed_token', None)
	if not unauthed_token:
		return HttpResponse("No un-authed token cookie")
	token = oauth.OAuthToken.from_string(unauthed_token)   
	if token.key != request.GET.get('oauth_token', 'no-token'):
		return HttpResponse("Something went wrong! Tokens do not match")
	access_token = exchange_request_token_for_access_token(CONSUMER, CONNECTION, token)
	request.session['access_token'] = access_token.to_string()
	next = request.session.get('return_url')
	if next:
		return HttpResponseRedirect(next)
	return HttpResponseRedirect(reverse('twitter_oauth_main'))

@render_to('twitter_app/list.html')
@oauth_required
def friend_list(request):
	twit = request.twitter
	creds = request.creds
	
	name = creds.get('name', creds['screen_name']) # Get the name
	
	# Get number of friends. The API only returns 100 results per page,
	# so we might need to divide the queries up.
	friends_count = int(creds.get('friends_count', '100'))
	pages = int(friends_count // 100 + 1)
	pages = min(pages, 10) # We only want to make ten queries
	
	users = []
	
	for page in range(pages):
		friends = twit.get_friends(page+1)
		if friends:
			users.append(friends)
		else:
			break

	return {'users': users}

@render_to('twitter_app/status.html')
@oauth_required
def status(request):
	if request.method == 'POST' and 'text' in request.POST:
		text = request.POST['text']
		r = request.twitter.set_status(text)
		return redirect('twitter-home')
	timeline = request.twitter.get_user_timeline()
	return {'timeline':timeline}

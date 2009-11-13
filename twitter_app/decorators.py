from django.shortcuts import redirect
from .utils import TwitterClient
import oauth

def oauth_required(view):
	def fn(request, *args, **kargs):
		auth = None
		access_token = request.session.get('access_token', None)
		if access_token:
			token = oauth.OAuthToken.from_string(access_token)
			twitter = TwitterClient(token)
			auth = twitter.is_authenticated()
			if auth:
				request.twitter = twitter
				request.creds = auth
				request.token = token
				return view(request, *args, **kargs)
		request.session['next'] = request.GET.get('next')
		request.session['return_url'] = request.path
		return redirect('twitter_oauth_auth')
	return fn

from django.conf import settings
import urllib2, urllib
from .twython import setup

"""
YQL_URL = getattr(settings, 'YQL_URL', 'https://query.yahooapis.com/v1/public/yql')
YQL_ENV = getattr(settings, 'YQL_ENV', 'http://datatables.org/alltables.env')

TWITTER_POST = 'insert into twitter.status (status,username,password) values ("%(status)s","%(username)s","%(password)s")'

def yql(query):
	data = {
		'q':query,
		'env':YQL_ENV,
		'diagnostics':'false',
		'format':'json',
	}
	response = urllib2.urlopen(YQL_URL, urllib.urlencode(data))
	r = response.read()
	return r
"""

def user_tweet(username, password, status):
	twitter = setup(username=username, password=password)
	return twitter.updateStatus(status)

def global_tweet(status):
	return user_tweet(settings.TWITTER_USERNAME, settings.TWITTER_PASSWORD, status)

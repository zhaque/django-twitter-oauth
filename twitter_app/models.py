from django.db import models
from django.contrib.auth.models import User
from twython import setup
import simplejson, datetime

TWITTER_PROFILE_CACHE_TIME = 5 # minutes

def _get_twitter_profile(self):
	try:
		tp = TwitterProfile.objects.get(user=self)
		if datetime.datetime.now() > tp.date_updated + datetime.timedelta(minutes=TWITTER_PROFILE_CACHE_TIME):
			tp.update()
			tp.save()
		return tp.profile
	except TwitterProfile.DoesNotExist:
		tp = TwitterProfile()
		tp.user = self
		tp.update()
		tp.save()
		return tp.profile
User.twitter_profile = property(_get_twitter_profile)

class TwitterProfile(models.Model):
	user = models.ForeignKey(User)
	date_updated = models.DateTimeField(auto_now_add=True)
	profile_data = models.TextField(default='{}')
	
	def update(self):
		self.date_updated = datetime.datetime.now()
		twitter = setup()
		self.profile = twitter.showUser(screen_name=unicode(self.user.username))
	
	def get_data(self):
		return simplejson.loads(self.profile_data)
		
	def set_data(self, v):
		self.profile_data = simplejson.dumps(v)
	
	profile = property(get_data, set_data)

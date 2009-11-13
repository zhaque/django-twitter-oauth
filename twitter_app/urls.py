from django.conf.urls.defaults import *

from twitter_app.views import *

urlpatterns = patterns('twitter_app.views',
    url(r'^$',
        view=main,
        name='twitter_oauth_main'),
		
    url(r'^login/$',
        view=login_,
        name='twitter_oauth_login'),
    
    url(r'^auth/$',
        view=auth,
        name='twitter_oauth_auth'),

    url(r'^unauth/$',
        view=unauth,
        name='twitter_oauth_unauth'),

    url(r'^return/$',
        view=return_,
        name='twitter_oauth_return'),
  
    url(r'^list/$',
        view=friend_list,
        name='twitter_oauth_friend_list'),
		
    url(r'^status/$',
        view=status,
        name='twitter-home'),
)

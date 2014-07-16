import ipdb
from datetime import datetime
import time

from open_facebook import OpenFacebook

from .models import UserProfile

    # User details pipeline
def user_details(strategy, details, response, user=None, is_new=False, *args, **kwargs):
    """Update user details using data from provider."""
    print "are you working"
    if user:
        if is_new:
            if strategy.backend.name == 'facebook':
                token = response['access_token']
                graph = OpenFacebook(token) 
                locale = response['locale']
                hometown = response['hometown']['name'] 
                birthday = datetime.strptime(response['birthday'], "%m/%d/%Y").strftime("%Y-%m-%d")
                location = response['location']['name']
                photo = "http://graph.facebook.com/%s/picture?type=large" % response['id']
                try:
                    profile = user.userprofile
                except UserProfile.DoesNotExist:  
                    profile = UserProfile(user=user, birthday=birthday)   
                finally: 
                    profile.location = location
                    profile.hometown = hometown
                    profile.locale = locale
                    profile.photo_url = photo 
                    profile.save() 

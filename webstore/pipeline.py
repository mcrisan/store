import ipdb
from datetime import datetime
import time

from .models import UserProfile

    # User details pipeline
def user_details(strategy, details, response, user=None, is_new=False, *args, **kwargs):
    """Update user details using data from provider."""
    if user:
        if is_new:
            if strategy.backend.name == 'facebook':
                token = response['access_token']
                locale = response['locale']
                hometown = response['hometown']['name'] 
                birthday = datetime.strptime(response['birthday'], "%m/%d/%Y").strftime("%Y-%m-%d")
                location = response['location']['name']
                photo = "http://graph.facebook.com/%s/picture?type=large" % response['id']
            elif strategy.backend.name == 'twitter': 
                photo = response['profile_image_url']
                location =""
                hometown =""
                locale = ""
                birthday = None
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
      

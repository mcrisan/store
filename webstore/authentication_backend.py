from django.contrib.auth.backends import ModelBackend
from social.backends.twitter import TwitterOAuth
from social.backends.facebook import Facebook2OAuth2
from .models import ProxyUser

class ProxyUserBackend(ModelBackend):
    
    def authenticate(self,username=None,password=None):
        try:
            user = ProxyUser.objects.get(username=username)
        except ProxyUser.DoesNotExist:
            user = None
        if user is not None and user.check_password(password):
            return user
        return None
    
    def get_user(self,user_id):
        try:
            return ProxyUser.objects.get(pk=user_id)
        except ProxyUser.DoesNotExist:
            return None
        
class TwitterBackend(TwitterOAuth):
       
    def get_user(self,user_id):
        try:
            return ProxyUser.objects.get(pk=user_id)
        except ProxyUser.DoesNotExist:
            return None    
        
class FacebookBackend(Facebook2OAuth2):
       
    def get_user(self,user_id):
        try:
            return ProxyUser.objects.get(pk=user_id)
        except ProxyUser.DoesNotExist:
            return None       
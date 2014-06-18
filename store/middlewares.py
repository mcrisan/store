import os
from uuid import getnode as get_mac
from django.contrib.auth.models import User

class UserMiddleware(object):

    def process_request(self, request):
        if not request.user.is_authenticated():
            unumber = os.getuid()
            mac = get_mac()
            if 'user_id' not in request.session:
                request.session['user_id'] = mac
                #user = User.objects.filter(username=mac).first()
                #if not user:
                #   user = User(username=mac, first_name='Anonymous', last_name='User')
                #   user.set_unusable_password()
                #   user.save()       
        return 
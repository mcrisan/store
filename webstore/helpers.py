import hashlib

from django.utils.http import urlquote

from django.contrib.auth.models import User

def get_user(request):
    current_user = check_user(request)
    if not current_user:
        current_user = User(username=request.session['user_id'][0:15], 
                            first_name='Anonymous', 
                            last_name=request.session['user_id'][15:])
        current_user.set_unusable_password()
        current_user.save()
    return current_user 

def check_user(request):
    if request.user.is_authenticated():
        current_user = request.user
    else:
        try:
            current_user = (User.objects.filter(username=request.session['user_id'][0:15], 
                                                last_name=request.session['user_id'][15:])
                                       .first())
        except KeyError:
           current_user=None 
    return current_user 


def template_cache_key(fragment_name, *vary_on):
    """Builds a cache key for a template fragment.

    This is shamelessly stolen from Django core.
    """
    base_cache_key = "template.cache.%s" % fragment_name
    args = hashlib.md5(u":".join([urlquote(var) for var in vary_on]))
    return "%s.%s" % (base_cache_key, args.hexdigest())
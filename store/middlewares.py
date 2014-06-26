import uuid


class UserMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            if 'user_id' not in request.session:
                user_id = uuid.uuid4().get_hex()
                request.session['user_id'] = user_id     
import functools

from google.appengine.api import users

def require_login_or_fail(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = users.get_current_user()
        if not user:
            self.error(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper
def require_login_or_redirect(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = users.get_current_user()
        if not user:
            if self.request.method == "GET": #otherwise we want to show we failed
                self.redirect(users.create_login_url(self.request.uri))
                return
            else:
                self.error(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper

import functools
import logging

from google.appengine.api import users
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json


from models import Bookmark, Link

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


class BookmarkHandler(webapp.RequestHandler):
    @require_login_or_redirect
    def get(self):
        g = self.request.get
        q = Bookmark.all()
        if g('tag'):
            q = q.filter('user_tags=', g('tag'))
        if g('tags'): #union comma sep
            q = q.filter('user_tags IN', g('tags').split(','))
        if g('all_tags'):
            for t in g('all_tags').split(','):
                q = q.filter('user_tags=', t)
        
        def has_permission_for(r):
            return (r.access == 'public' or r.user == users.get_current_user())

        results = [r for r in q.fetch(10) if has_permission_for(r)]


        self.response.out.write([r.link.url for r in results])

    @require_login_or_fail
    def post(self):
        url = self.request.get('link')
        l = Link.all().filter('url =', url).get()
        if l is None:
            l = Link(url=url)
            l.put()

        b = Bookmark(
            user = users.get_current_user(),
            title = self.request.get('title'),
            link = l,
            user_tags = [db.Category(t) for t in self.request.get('tags').split()], #tags whitespace separated
            access = self.request.get('access'))
        b.put()
        logging.info("new bookmark created - %s" % b)

    put = post #RESTful omg buzzword

    def delete(self):
        key = self.request.get('key')
        b = Bookmark.get(key)
        if not b:
            self.error(404) #this thing didn't exist
        if b.user != users.get_current_user:
            self.error(403) #tut tut
        else:
            b.delete()
    
            

application = webapp.WSGIApplication(
    [('/api*', BookmarkHandler)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

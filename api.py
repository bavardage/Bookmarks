import logging

from google.appengine.api import users
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app



from models import Bookmark, Link
from decorators import *
from jsonhandler import JSONHandler

FORBIDDEN = 403
NOT_FOUND = 404

class BookmarkHandler(JSONHandler):
    _model = Bookmark

    def get_link(self, url):
        l = Link.all().filter('url =', url).get()
        if l is None:
            l = Link(url=url)
            l.put()
        return l

    def has_permission_for(self, r):
        return (r.access == 'public' or r.user == users.get_current_user())

    def get(self):
        g = self.request.get
        q = Bookmark.all()
        if g('key'):
            b = Bookmark.get(g('key'))
            if b:
                if self.has_permission_for(b):
                    self.json_output([b,])
                    return
                else:
                    self.error(FORBIDDEN)
            else:
                self.error(NOT_FOUND)
        if g('tag'):
            q = q.filter('user_tags=', g('tag'))
        if g('tags'): #union comma sep
            q = q.filter('user_tags IN', g('tags').split(','))
        if g('all_tags'):
            for t in g('all_tags').split(','):
                q = q.filter('user_tags=', t)
        if g('link'):
            l = Link.all().filter('url=', g('link')).get()
            if l:
                q = q.filter('link=', l)
        if g('title'):
            q = q.filter('title=', g('title'))
        if g('access'):
            q = q.filter('access=', g('access'))
        if g('user'):
            q = q.filter('user=', user) #TODO: see if we must get user from db
        
        results = [r for r in q.fetch(10) if self.has_permission_for(r)]
        self.json_output(results)

    @require_login_or_fail
    def post(self):
        g = self.request.get
        l = self.get_link(g('link'))
        b = Bookmark(
            user = users.get_current_user(),
            title = g('title'),
            link = l,
            user_tags = [db.Category(t) for t in g('user_tags').split()], 
            #tags whitespace separated
            access = g('access'))
        b.put()
        logging.info("new bookmark created - %s" % b)

    @require_login_or_fail
    def put(self):
        g = self.request.get
        b = self.Bookmark.get('key')
        if b is None:
            self.post()
        else:
            if b.user == users.get_current_user():
                if g('title'): b.title = g('title')
                if g('link'): b.link = self.get_link(g('link'))
                if g('user_tags'): b.user_tags = [db.Category(t) for t in g('user_tags')]
                if g('access'): b.access = g('access')
            else:
                self.error(FORBIDDEN)
            
application = webapp.WSGIApplication(
    [('/api*', BookmarkHandler)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

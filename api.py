import logging

from google.appengine.api import users
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app



from models import Bookmark, Link
from decorators import *
from jsonhandler import JSONHandler
from users import get_friendship

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

    def can_view(self, r):
        if r.access == 'public':
            return True
        elif r.user == users.get_current_user():
            return True
        else:
            fs = get_friendship(r.user, users.get_current_user())
            if fs and fs.type == 'friendship':
                return True
            else: 
                return False

    @require_login_or_fail
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
                    self.do_error('forbidden')
            else:
                self.do_error('not-found')
        if g('tag'):
            q = q.filter('tags=', g('tag'))
        if g('tags'): #union comma sep
            q = q.filter('tags IN', g('tags').split(','))
        if g('all_tags'):
            for t in g('all_tags').split(','):
                q = q.filter('tags=', t)
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

        q = q.order('-created')

        try:
            limit = int(g('limit'))
        except:
            limit = 10

        results = [r for r in q.fetch(limit) if self.can_view(r)]
        self.json_output(results)

    #TODO: SCRUB TITLE MAJORLY FOR <script etc
    @require_login_or_fail
    def post(self):
        g = self.request.get
        l = self.get_link(g('link'))
        b = Bookmark(
            user = users.get_current_user(),
            title = g('title'),
            link = l,
            tags = [db.Category(t) for t in g('tags').split()], 
            #tags whitespace separated
            access = g('access'))
        b.put()
        logging.info("new bookmark created - %s" % b)

    @require_login_or_fail
    def put(self):
        g = self.request.get
        b = Bookmark.get(g('key'))
        if b is None:
            self.post()
        else:
            if b.user == users.get_current_user():
                if g('title'): b.title = g('title')
                if g('link'): b.link = self.get_link(g('link'))
                if g('tags'): b.tags = [db.Category(t) for t in g('tags').split()]
                if g('access'): b.access = g('access')
                b.put()
            else:
                self.do_error('forbidden')
            
application = webapp.WSGIApplication(
    [('/api/bookmarks.*', BookmarkHandler)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

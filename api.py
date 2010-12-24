import logging

from google.appengine.api import users
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app



from models import Bookmark, Link
from decorators import *
from jsonhandler import JSONHandler



class BookmarkHandler(JSONHandler):
    _model = Bookmark

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
        
        def has_permission_for(r):
            return (r.access == 'public' or r.user == users.get_current_user())

        results = [r for r in q.fetch(10) if has_permission_for(r)]
        json_output = self.JSONEncoder().encode(results)
        self.response.out.write(json_output)

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
    
            

application = webapp.WSGIApplication(
    [('/api*', BookmarkHandler)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

import logging, os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class UIHandler(webapp.RequestHandler):
    def render_template(self, path):
        tp = os.path.join(os.path.dirname(__file__), 'html', path)
        logging.debug("rendering template at %s" % tp)
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
        else:
            url = users.create_login_url(self.request.uri)
            
        params = {'user': user, 'login_logout_url': url}
        self.response.out.write(template.render(tp, params))
    
    def get(self, path):
        paths = {'': 'index.html'}
        if path in paths:
            self.render_template(paths[path])
        else:
            self.error(404)

application = webapp.WSGIApplication(
    [('/(.*)', UIHandler)],
    debug=True) #TODO: change debugs!

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

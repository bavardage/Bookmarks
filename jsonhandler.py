import logging, datetime

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from django.utils import simplejson as json

class JSONHandler(webapp.RequestHandler):
    _model = None

    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            date_serialiser = lambda d : d.ctime()
            user_serialiser = lambda u : {'nickname': u.nickname(),
                                          'email': u.email()} if u else None
            serialisers = {datetime.datetime: date_serialiser,
                           users.User: user_serialiser}
            if obj.__class__ in serialisers:
                return serialisers[obj.__class__](obj)
            elif isinstance(obj, db.Model):
                output = {}
                for k,v in obj.properties().iteritems():
                    val = getattr(obj, k)
                    output[k] = val
                return output
            else:
                raise TypeError("Can't serialise %s of type %s" % (obj, obj.__class__))
    #end JSONEncoder#############

    def delete(self):
        key = self.request.get('key')
        b = self._model.get(key)
        if not b:
            self.error(404) #this thing didn't exist
        if b.user != users.get_current_user: #this means no login required perse
            self.error(403) #tut tut
        else:
            b.delete()

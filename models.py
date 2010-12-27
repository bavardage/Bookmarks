from google.appengine.ext import db

class Link(db.Model):
    url = db.LinkProperty(required=True)
    #other social stuff?


class Bookmark(db.Model):
    '''
    Each bookmark is associated with one and only one user.
    It has a Link which is where social aspects could happen!
    '''
    user = db.UserProperty()
    title = db.StringProperty(required=True)
    link = db.ReferenceProperty(Link, required=True)
    tags = db.ListProperty(db.Category)
    created = db.DateTimeProperty(auto_now_add=True)
    access = db.StringProperty(required=True, choices=set(["public", "friends", "private"]))

class Friendship(db.Model):
    '''
    Representing some form of connection (symmetric?)
    Apparently this is a bad way to model such connections, since it's
    innefficient, BUT then again, that was with ReferenceProperty rather
    than UserProperty
    '''
    fr = db.UserProperty(required=True) #request FROM user TO user
    to = db.UserProperty(required=True)
    status = db.StringProperty(required=True, 
                               choices=set(["friendship", "request", "block"]))
    created = db.DateTimeProperty(required=True, auto_now_add=True)

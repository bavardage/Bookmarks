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
    user_tags = db.ListProperty(db.Category)
    created = db.DateTimeProperty(auto_now_add=True)
    access = db.StringProperty(required=True, choices=set(["public", "friends", "private"]))


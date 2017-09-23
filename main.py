import webapp2
import os
import jinja2

from google.appengine.api import users
from google.appengine.ext import ndb

import logging

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

#==================MODELS=======================

class Post(ndb.Model):
    user_email = ndb.StringProperty()
    post_time = ndb.DateTimeProperty(auto_now_add=True)
    title = ndb.StringProperty()
    text = ndb.StringProperty()
    relate_count = ndb.IntegerProperty(default=0)
    view_count = ndb.IntegerProperty(default=0)
    recent_view_count = ndb.IntegerProperty(default=0)
    approved = ndb.BooleanProperty(default=True)
    flagged = ndb.BooleanProperty(default=False)
    clearFlag = ndb.BooleanProperty(default=False)
    tags = ndb.StringProperty(repeated=True)

class Comment(ndb.Model):
    user = ndb.StringProperty()
    content = ndb.StringProperty()
    post_time = ndb.DateTimeProperty(auto_now_add = True)
    post_key = ndb.KeyProperty(kind=Post)

class View(ndb.Model):
    user = ndb.StringProperty()
    post_key = ndb.KeyProperty(kind=Post)
    view_time = ndb.DateTimeProperty(auto_now_add=True)

class Flag(ndb.Model):
    user = ndb.StringProperty()
    post_key = ndb.KeyProperty(kind=Post)
    flagged = ndb.BooleanProperty()
    flag_time = ndb.DateTimeProperty(auto_now_add=True)
    #true = flagged, false = not flagged

#=================HANDLERS===========================

class MainHandler(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        login_url = users.create_login_url('/')
        logout_url = users.create_logout_url('/')
        #order trending
        posts = Post.query().order(-Post.recent_view_count).fetch()
        template_vars = {
            "posts": posts,
            "current_user": current_user,
            "logout_url": logout_url,
            "login_url": login_url
        }
        template = jinja_environment.get_template('home.html')
        self.response.write(template.render(template_vars))

class ArchiveHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('archive.html')
        self.response.write(template.render())

class NewPostHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('newpost.html')
        self.response.write(template.render())

class ResourcesHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('resources.html')
        self.response.write(template.render())

class AboutHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('about.html')
        self.response.write(template.render())

class PostHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('post.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/archive', ArchiveHandler),
    ('/archive.html', ArchiveHandler),
    ('/newpost', NewPostHandler),
    ('/newpost.html', NewPostHandler),
    ('/resources', ResourcesHandler),
    ('/resources.html', ResourcesHandler),
    ('/about', AboutHandler),
    ('/about.html', AboutHandler),
    ('/post', PostHandler),
    ('/post.html', PostHandler),
], debug=True)

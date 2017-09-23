import webapp2
import os
import jinja2

from google.appengine.api import users
from google.appengine.ext import ndb

import logging

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('home.html')
        self.response.write(template.render())

class ArchiveHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('archive.html')
        self.response.write(template.render())

class NewPostHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('new_post.html')
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
    ('/new_post', NewPostHandler),
    ('/resources', ResourcesHandler),
    ('/about', AboutHandler),
    ('/post', PostHandler)
], debug=True)

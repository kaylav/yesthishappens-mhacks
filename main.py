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
        #self.response.write('Hello world!!!!')

        template = jinja_environment.get_template('home.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)

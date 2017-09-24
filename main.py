#TODO: Search bar in archive/ filter by tags
#TODO: Get flag button working 

import webapp2
import os
import jinja2
import datetime

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
    disrelate_count = ndb.IntegerProperty(default=0)
    view_count = ndb.IntegerProperty(default=0)
    recent_view_count = ndb.IntegerProperty(default=0)
    approved = ndb.BooleanProperty(default=True)
    flagged = ndb.BooleanProperty(default=False)
    clearFlag = ndb.BooleanProperty(default=False)
    tags = ndb.StringProperty(repeated=True)

class ReactionType(ndb.Model):
    user = ndb.StringProperty()
    post_key = ndb.KeyProperty(kind=Post)
    rating_type = ndb.BooleanProperty()
    reaction_time = ndb.DateTimeProperty(auto_now_add=True)
    #true = relate, false = disrelate

class Comment(ndb.Model):
    user = ndb.StringProperty()
    content = ndb.StringProperty()
    post_time = ndb.DateTimeProperty(auto_now_add = True)
    post_key = ndb.KeyProperty(kind=Post)

class View(ndb.Model):
    user = ndb.StringProperty()
    post_key = ndb.KeyProperty(kind=Post)
    view_time = ndb.DateTimeProperty(auto_now_add=True)

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
        posts = Post.query().fetch()
        template_vars = {
            "posts": posts
        }
        template = jinja_environment.get_template('archive.html')
        self.response.write(template.render(template_vars))

class NewPostHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            logout_url = users.create_logout_url('/')
            template_vals ={'logout_url':logout_url}
            template = jinja_environment.get_template('newpost.html')
            self.response.write(template.render(template_vals))
            logging.info(user.email())

        else:
            login_url = users.create_login_url('/')
            template = jinja_environment.get_template("login.html")
            template_vals = {'login_url':login_url}
            self.response.write(template.render(template_vals))

    def post(self):
        user = users.get_current_user()
        email = user.email().lower()

        title = self.request.get('title')
        text = self.request.get('text')

        tags = self.request.get_all('tags')
        logging.info(tags)
        self.redirect('/newpost')


        post = Post(title = title, text = text, user_email = email, tags = tags)
        post.put()



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
        #1. Get information from the request
        urlsafe_key = self.request.get("key")
        #2. Pulling the post from the database
        post_key = ndb.Key(urlsafe = urlsafe_key)
        post = post_key.get()
        current_user = users.get_current_user()
        #query, fetch, and filter the comments
        comments = Comment.query().filter(Comment.post_key == post_key).order(Comment.post_time).fetch()
        #Get the number of relates, filter them by post key
        #relates = Relate.query().filter(Relate.post_key == post_key).fetch()

        #==view counter==
        post.view_count += 1
        post.put()
        views = View.query().fetch()
        if current_user:
            view = View(user=current_user.email(), post_key=post_key)
            view.put()
            #===trending calculations===
        # view = View.query().fetch()
        # time_difference = datetime.datetime.now() - datetime.timedelta(hours=2)
        # # for post in posts:
        # post_key = post.key.urlsafe()
        # post.recent_view_count = 0
        # for view in views:
        #     if view.post_key.urlsafe() == post_key and view.view_time > time_difference:
        #         post.recent_view_count += 1
        #         post.recent_view_count = post.recent_view_count * post.relate_count
        #         post.put()

        template_vars = {
            "post": post,
            "comments": comments,
            "current_user": current_user,
            'views': views
        }
        template = jinja_environment.get_template("post.html")
        self.response.write(template.render(template_vars))

class RelateHandler(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user().email()

        #1. Getting information from the request
        urlsafe_key = self.request.get("post_key")
        #2. Interacting with our Database and APIs
        post_key = ndb.Key(urlsafe = urlsafe_key)
        post = post_key.get()
        reaction = ReactionType.query().filter(ndb.AND(ReactionType.post_key == post_key, ReactionType.user == current_user)).order(-ReactionType.reaction_time).get()
        if reaction:
            if reaction.rating_type == False:
                post.disrelate_count = post.disrelate_count - 1
                post.relate_count = post.relate_count + 1
                post.put()
                reaction = ReactionType(user=current_user, rating_type=True, post_key=post_key)
                reaction.put()
        else:
            post.relate_count = post.relate_count + 1
            post.put()
            reaction = ReactionType(user=current_user, rating_type=True, post_key=post_key)
            reaction.put()


        # === 3: Send a response. ===
        # Send the updated count back to the client.
        url = "/post?key=" + post.key.urlsafe()
        self.redirect(url)

class DisrelateHandler(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user().email()
        #1. Getting information from the request
        urlsafe_key = self.request.get("post_key")
        #2. Interacting with our Database and APIs
        post_key = ndb.Key(urlsafe = urlsafe_key)
        post = post_key.get()
        reaction = ReactionType.query().filter(ndb.AND(ReactionType.post_key == post_key, ReactionType.user == current_user)).order(-ReactionType.reaction_time).get()
        if reaction:
            if reaction.rating_type == True:
                post.relate_count = post.relate_count - 1
                post.disrelate_count = post.disrelate_count + 1
                post.put()
                reaction = ReactionType(user=current_user, rating_type=False, post_key=post_key)
                reaction.put()
        else:
            post.disrelate_count = post.disrelate_count + 1
            post.put()
            reaction = ReactionType(user=current_user, rating_type=False, post_key=post_key)
            reaction.put()

         # Increase the photo count and update the database.


        # === 3: Send a response. ===
        # Send the updated count back to the client.
        url = "/post?key=" + post.key.urlsafe()
        self.redirect(url)

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
    ('/relate', RelateHandler),
    ('/disrelate', DisrelateHandler),
    ('/post', PostHandler),
    ('/post.html', PostHandler),
], debug=True)

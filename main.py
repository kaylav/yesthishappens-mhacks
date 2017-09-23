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
    like_count = ndb.IntegerProperty(default=0)
    dislike_count = ndb.IntegerProperty(default=0)
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

class LikeType(ndb.Model):
    user = ndb.StringProperty()
    post_key = ndb.KeyProperty(kind=Post)
    rating_type = ndb.BooleanProperty()
    like_time = ndb.DateTimeProperty(auto_now_add=True)
    #true = like, false = dislike

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
        #1. Get information from the request
        urlsafe_key = self.request.get("key")
        #2. Pulling the post from the database
        post_key = ndb.Key(urlsafe = urlsafe_key)
        post = post_key.get()
        current_user = users.get_current_user()
        #query, fetch, and filter the comments
        comments = Comment.query().filter(Comment.post_key == post_key).order(Comment.post_time).fetch()
        #Get the number of likes, filter them by post key
        #likes = Like.query().filter(Like.post_key == post_key).fetch()

        #==view counter==
        post.view_count += 1
        post.put()
        views = View.query().fetch()
        if current_user:
            view = View(user=current_user.email(), post_key=post_key)
            view.put()
            #===trending calculations===
        views = View.query().fetch()

        views = View.query().fetch()
        time_difference = datetime.datetime.now() - datetime.timedelta(hours=2)
        # for post in posts:
        post_key = post.key.urlsafe()
        post.recent_view_count = 0
        for view in views:
            if view.post_key.urlsafe() == post_key and view.view_time > time_difference:
                post.recent_view_count += 1
                like_delta = post.like_count - post.dislike_count
                post.recent_view_count = post.recent_view_count * like_delta
                post.put()

        template_vars = {
            "post": post,
            "comments": comments,
            "current_user": current_user,
            'views': views,
        }
        template = jinja_environment.get_template("templates/post.html")
        self.response.write(template.render(template_vars))

class LikeHandler(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user().email()

        #1. Getting information from the request
        urlsafe_key = self.request.get("post_key")
        #2. Interacting with our Database and APIs
        post_key = ndb.Key(urlsafe = urlsafe_key)
        post = post_key.get()
        like = LikeType.query().filter(ndb.AND(LikeType.post_key == post_key, LikeType.user == current_user)).order(-LikeType.like_time).get()
        if like:
            if like.rating_type == False:
                post.dislike_count = post.dislike_count - 1
                post.like_count = post.like_count + 1
                post.put()
                like = LikeType(user=current_user, rating_type=True, post_key=post_key)
                like.put()
        else:
            post.like_count = post.like_count + 1
            post.put()
            like = LikeType(user=current_user, rating_type=True, post_key=post_key)
            like.put()


        # === 3: Send a response. ===
        # Send the updated count back to the client.
        url = "/post?key=" + post.key.urlsafe()
        self.redirect(url)

class DislikeHandler(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user().email()
        #1. Getting information from the request
        urlsafe_key = self.request.get("post_key")
        #2. Interacting with our Database and APIs
        post_key = ndb.Key(urlsafe = urlsafe_key)
        post = post_key.get()
        like = LikeType.query().filter(ndb.AND(LikeType.post_key == post_key, LikeType.user == current_user)).order(-LikeType.like_time).get()
        if like:
            if like.rating_type == True:
                post.like_count = post.like_count - 1
                post.dislike_count = post.dislike_count + 1
                post.put()
                like = LikeType(user=current_user, rating_type=False, post_key=post_key)
                like.put()
        else:
            post.dislike_count = post.dislike_count + 1
            post.put()
            like = LikeType(user=current_user, rating_type=False, post_key=post_key)
            like.put()

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
    ('/post', PostHandler),
    ('/post.html', PostHandler),
    ('/like', LikeHandler),
    ('/like.html', LikeHandler),
    ('/dislike', DislikeHandler),
    ('/dislike.html', DislikeHandler),
], debug=True)

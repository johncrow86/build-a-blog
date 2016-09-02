import webapp2
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):

    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

class Postsdb(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        self.redirect("/blog")

class Blog(Handler):
    def get(self):
        blog_posts = db.GqlQuery("SELECT * FROM Postsdb order by created desc limit 5")

        t = jinja_env.get_template("blog.html")
        response = t.render(posts = blog_posts)
        self.response.write(response)

class NewPost(Handler):
    def get(self):
        t = jinja_env.get_template("newpost.html")
        response = t.render()
        self.response.write(response)

    def post(self):
        post_title = self.request.get("title")
        post_body = self.request.get("body")

        # check for empty title or body and render same page
        if (not post_title) or (post_title.strip() == "") or (not post_body) or (post_body.strip() == ""):
            error = "Please enter a title and a post"
            t = jinja_env.get_template("newpost.html")
            response = t.render(title=post_title, body=post_body, error=error)
            self.response.write(response)
        # store the post inthe database and redirect home
        else:
            p = Postsdb(title = post_title, body = post_body)
            p.put()
            self.redirect("/")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', Blog),
    ('/newpost', NewPost)
], debug=True)

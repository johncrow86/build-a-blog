import webapp2
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def get_posts(limit, offset):
    return db.GqlQuery("SELECT * FROM Postsdb order by created desc limit %s offset %s" % (limit, offset))

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
        page = 1
        if self.request.get("page"):
            page = int(self.request.get("page"))
            offset_value = (page - 1) * 5
            blog_posts = get_posts(5, offset_value)
        else:
            offset_value = 0
            blog_posts = get_posts(5, offset_value)

        count = blog_posts.count(offset=offset_value)

        t = jinja_env.get_template("blog.html")
        response = t.render(posts=blog_posts, count=count, page=page)
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
        # store the post inthe database and redirect to the post
        else:
            p = Postsdb(title = post_title, body = post_body)
            p.put()
            self.redirect("/blog/" + str(p.key().id()))

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        blog_posts = Postsdb.get_by_id(int(id))

        t = jinja_env.get_template("singlepost.html")
        response = t.render(posts = blog_posts)
        self.response.write(response)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', Blog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

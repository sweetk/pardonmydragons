from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:AnyPassword@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))

    def __init__(self, title):
        self.title = title

    def post(self, body):
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blogs')

@app.route('/blogs', methods=['POST', 'GET'])
def blogs():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        #Error checking here?
        title_error = ''
        body_error = ''

        blog_title = request.form['blog_title']
        if blog_title == '':
            title_error = 'This post needs a title'
        new_blog = Blog(blog_title)

        blog_body = request.form['blog_body']
        if blog_body == '':
            body_error = 'This post needs a body'
        new_blog.post(blog_body)

        #TODO edit newpost so blog title and body are preserved
        if title_error != '' or body_error != '':
            return render_template('newpost.html', saved_title=blog_title, saved_body=blog_body, title_error=title_error, body_error=body_error)

        #If no errors
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blogs')

    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()

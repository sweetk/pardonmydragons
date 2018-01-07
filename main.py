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
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    blog_id = request.args.get('id')

    #Individual blog request
    if blog_id:
        blog_id = int(blog_id)
        return render_template('individualentry.html', blogs=blogs, blog_id=blog_id)

    #Full blog
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

        if title_error != '' or body_error != '':
            return render_template('newpost.html', saved_title=blog_title, saved_body=blog_body, title_error=title_error, body_error=body_error)

        #If no errors
        db.session.add(new_blog)
        db.session.commit()

        #id_num = new_blog.id

        return redirect('/blog?id=' + str(new_blog.id))

    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()

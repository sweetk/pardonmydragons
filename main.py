from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:guest@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ghakrRfPLSdwOOBt5678'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, owner):
        self.title = title
        self.owner = owner

    def post(self, body):
        self.body = body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # validate user's data
        if len(username) < 3:
            flash("Your username must be more than 3 characters.")
            return redirect('/register')
        if not password == verify:
            flash("Your passwords did not match, please try again")
            return redirect('/register')
        if len(password) < 3:
            flash("Your password must be more than 3 characters.")
            return redirect('/register')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("A user with that username already exists")
            return redirect('/register')

    return render_template('register.html')


@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    users = User.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user_id')

    #Individual blog request
    if blog_id:
        blog_id = int(blog_id)
        return render_template('individualentry.html', blogs=blogs, users=users, blog_id=blog_id)

    if user_id:
        user_id = int(user_id)
        return render_template('individualuser.html', blogs=blogs, users=users, user_id=user_id)

    #Full blog
    return render_template('blog.html', users=users, blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title_error = ''
        body_error = ''

        owner = User.query.filter_by(username=session['username']).first()

        blog_title = request.form['blog_title']
        if blog_title == '':
            title_error = 'This post needs a title'
        new_blog = Blog(blog_title, owner)

        blog_body = request.form['blog_body']
        if blog_body == '':
            body_error = 'This post needs a body'
        new_blog.post(blog_body)

        if title_error != '' or body_error != '':
            return render_template('newpost.html', saved_title=blog_title, saved_body=blog_body, title_error=title_error, body_error=body_error)

        #If no errors
        db.session.add(new_blog)
        db.session.commit()


        return redirect('/blog?id=' + str(new_blog.id))

    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()

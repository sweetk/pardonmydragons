from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
import requests, json

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://pardonmydragons:localhost@localhost:8889/pardonmydragons'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '09876trcvbnmki8u7y6tgbnmkiu87ytgbn'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    characters =  db.relationship('Character', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

class Character(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    charname = db.Column(db.String(120))
    charclass = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, charname, charclass, owner):
        self.charname = charname
        self.charclass = charclass
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index']
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
            return redirect('/') #Change to welcome?
        else:
            flash("A user with that username already exists")
            return redirect('/register')

    return render_template('register.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/')

@app.route('/charactercreation', methods=['POST', 'GET'])
def charactercreation():
    if request.method == 'POST':
        charname = request.form['charname']
        charclass = request.form['charclass']
        owner = User.query.filter_by(username=session['username']).first()

        if len(charname) < 1:
            flash("Please enter a Character Name.")
            return redirect('/charactercreation')
        else:
            new_char = Character(charname, charclass, owner)
            db.session.add(new_char)
            db.session.commit()
            return redirect(url_for('characterview', id = new_char.id))


    return render_template('charactercreation.html')

@app.route('/characterlist', methods=['GET'])
def characterlist():

    return render_template('characterlist.html')

@app.route('/characterview', methods=['GET'])
def characterview():
    id = request.args['id']
    current_char = Character.query.filter_by(id=id).first()

    return render_template('characterview.html', current_char=current_char)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        searchterm = request.form['searchterm']
        return redirect(url_for('SRD', searchterm = searchterm))

    response = requests.get("http://dnd5eapi.co/api/monsters")
    content = response.json()

    return render_template('search.html', content=content)

@app.route('/SRD', methods=['GET'])
def SRD():
    searchterm = request.args['searchterm']

    response = requests.get(searchterm)
    content = response.json()

    return render_template('SRD.html', content=content)

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()

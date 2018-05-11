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

## Table of Contents ##
# Classes
# login
# logout
# register
# character Creation
# character list
# character view
# search
# srd
# index

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
    charrace = db.Column(db.String(120))
    charclass = db.Column(db.String(120))
    #attributes
    strength = db.Column(db.Integer)
    dexterity = db.Column(db.Integer)
    constitution = db.Column(db.Integer)
    intelligence = db.Column(db.Integer)
    wisdom = db.Column(db.Integer)
    charisma = db.Column(db.Integer)
    #foreign keys
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, charname, charrace, charclass, owner):
        self.charname = charname
        self.charrace = charrace
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
            flash("Your username must be more than 3 characters.", 'error')
            return redirect('/register')
        if not password == verify:
            flash("Your passwords did not match, please try again", 'error')
            return redirect('/register')
        if len(password) < 3:
            flash("Your password must be more than 3 characters.", 'error')
            return redirect('/register')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/') #Change to welcome?
        else:
            flash("A user with that username already exists", 'error')
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
        charrace = request.form['charrace']
        charclass = request.form['charclass']
        owner = User.query.filter_by(username=session['username']).first()

        if len(charname) < 1:
            flash("Please enter a Character Name.", 'error')
            return redirect('/charactercreation')
        else:
            new_char = Character(charname, charrace, charclass, owner)
            db.session.add(new_char)
            db.session.commit()
            return redirect(url_for('characterview', id = new_char.id))

    #populate classes
    response = requests.get("http://dnd5eapi.co/api/classes")
    content_class = response.json()
    #populate races
    response = requests.get("http://dnd5eapi.co/api/races")
    content_race = response.json()

    return render_template('charactercreation.html', content_class=content_class, content_race=content_race)

@app.route('/characterlist', methods=['GET'])
def characterlist():
    current_user = User.query.filter_by(username=session['username']).first()
    to_list = current_user.characters

    return render_template('characterlist.html', to_list=to_list)

@app.route('/characterview', methods=['GET', 'POST'])
def characterview():
    #needed for both get and post requests
    id = request.args['id']
    current_char = Character.query.filter_by(id=id).first()

    #Update
    if request.method =='POST':
        #attributes
        current_char.strength = request.form['strength']
        current_char.dexterity = request.form['dexterity']
        current_char.constitution = request.form['constitution']
        current_char.intelligence = request.form['intelligence']
        current_char.wisdom = request.form['wisdom']
        current_char.charisma = request.form['charisma']

        db.session.commit()
        flash('Updated Attributes!')

    return render_template('characterview.html', current_char=current_char)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        searchterm = request.form['searchterm']
        return redirect(url_for('SRD', searchterm = searchterm))

    response = requests.get("http://dnd5eapi.co/api/races")
    content_races = response.json()
    response = requests.get("http://dnd5eapi.co/api/classes")
    content_classes = response.json()
    response = requests.get("http://dnd5eapi.co/api/spells")
    content_spells = response.json()
    response = requests.get("http://dnd5eapi.co/api/monsters")
    content_monsters = response.json()
    response = requests.get("http://dnd5eapi.co/api/equipment")
    content_equipment = response.json()

    return render_template('search.html', content_races=content_races, content_classes=content_classes, content_spells=content_spells, content_monsters=content_monsters, content_equipment=content_equipment)

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

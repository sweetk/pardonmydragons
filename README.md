# Pardon My Dragons
A site for users to import Dungeons and Dragons 5e characters, and access SRD info

## Motivation
I was tasked with creating a project that showcased 3-5 features in my chosen language for LaunchCode's LiftOff Course. This project would enable me to begin the apprenticeship placement process on my way towards getting a job in tech. I chose to create a project about Dungeons and Dragons because It is something I'm passionate about, taking up a good percentage of my free time. I also wanted to learn how to use APIs, and I found a D&D 5e API that was simple and accessible.

## Screenshots
I'll include these later when the project is in a more finished state.

## Built With
- [Python](https://www.python.org/)
- [Jinja2](http://jinja.pocoo.org/)
- [Flask](http://flask.pocoo.org/)
- [MAMP](https://www.mamp.info/en/)

## Features
- Login/Logout
- Secure Password Storage
- Explore D&D 5e Reference Documents with Integrated API
- Create Characters Ready for Play

## Code Example
```python
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
            flash(charname + " the " + charclass + " has been saved to the database!")
```

## API Reference

[D&D 5e API](http://www.dnd5eapi.co/)

## Credits
[LaunchCode](https://www.launchcode.org/) both inspired me to build this project, and taught me much of the code necessary to do so. The very base code and user functionality were both built as taught to me in class, LaunchCode101.

## License
You can use this however you'd like, or:

MIT © [KJ Sweet](https://github.com/sweetk/pardonmydragons/blob/master/LICENSE)

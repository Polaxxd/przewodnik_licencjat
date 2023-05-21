from flask import Flask
from flask import render_template
from flask import flash
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "przewodnik_pola"
#Add database
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://20_palonek:polap1103@127.0.0.1/20_palonek'
# Initialize The Database
db.init_app(app)

# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    nick = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

# Create a Form Class to add users
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    nick = StringField("Nick", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class NamerForm(FlaskForm):
    Nname = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/')
def home():
    return render_template('home.htm')

@app.route('/kultura')
def kultura():
    return render_template('kultura.htm')

@app.route('/daktylografia')
def daktylografia():
    return render_template('daktylografia.htm')

@app.route('/daktylografia/teoria')
def daktylografia_teoria():
    return render_template('teoria.htm')

@app.route('/o_serwisie')
def o_serwisie():
    return render_template('o_serwisie.htm')


# Create Name Page
@app.route('/uzytkownik', methods=['GET', 'POST'])
def name():
    # Nname = None

    Nname = None
    Nform = NamerForm()
    # Validate Form
    if Nform.validate_on_submit():
        Nname = Nform.Nname.data
        Nform.Nname.data = ''
        flash("Form Submitted Successfully!")


    return render_template("name.htm",
                           Nname=Nname,
                           Nform=Nform)

@app.route('/uzytkownik/dodaj', methods=['GET', 'POST'])
def add_user():
    name = None
    added = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(nick=form.nick.data).first()
        if user is None:
            user = Users(name=form.name.data, nick=form.nick.data)
            db.session.add(user)
            db.session.commit()
            flash("Dodano użytkownika!")
            added = "tak"
        else:
            flash("Użytkownik o tym nicku już istnieje. Wybierz inną nazwę użytkownika.")
        name = form.name.data
        form.name.data = ''
        form.nick.data = ''
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.htm",
        form=form,
        name=name,
        our_users=our_users)

@app.route('/uzytkownik/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    edited = None
    if request.method == "POST":
        user = Users.query.filter_by(nick=form.nick.data).first()
        if user == name_to_update.nick:
            user=None
        if user is None:
            name_to_update.name = request.form['name']
            name_to_update.nick = request.form['nick']
            try:
                db.session.commit()
                flash("Zmieniono dane.")
                edited = "tak"
                return render_template("edytuj.htm",
                                       form = form,
                                       name_to_update = name_to_update)
            except:
                flash("Wystąpił błąd, spróbuj ponownie.")
                return render_template("edytuj.htm",
                                       form=form,
                                       name_to_update=name_to_update)
        else:
            flash("Użytkownik o tym nicku już istnieje. Wybierz inną nazwę użytkownika.")
    else:
        return render_template("edytuj.htm",
                                form=form,
                                name_to_update=name_to_update)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.htm'), 404

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()



# ssh 20_palonek@limba.wzks.uj.edu.pl -p 4016
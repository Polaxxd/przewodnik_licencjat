from flask import Flask
from flask import render_template
from flask import flash
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = "przewodnik_pola"
#Add database
db = SQLAlchemy()
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://20_palonek:polap1103@127.0.0.1/20_palonek'
# Initialize The Database
db.init_app(app)

# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    nick = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Passwords
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Hasło nie może być wyświetlone.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name


################## FORMS #####################
# Create a Form Class to add and update users
class UserForm(FlaskForm):
    name = StringField("Imię", validators=[DataRequired()])
    nick = StringField("Nick", validators=[DataRequired()])
    password_hash = PasswordField('Hasło', validators=[DataRequired(), EqualTo('password_hash2', message="Hasła muszą być takie same!")])
    password_hash2 = PasswordField('Powtórz hasło', validators=[DataRequired()])
    submit = SubmitField("Zapisz")

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

@app.route('/logowanie')
def login():
    return render_template('user.htm')

@app.route('/uzytkownik', methods=['GET', 'POST'])
def name():
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
            #hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, nick=form.nick.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash("Dodano użytkownika!")
            added = "tak"
        else:
            flash("Użytkownik o tym nicku już istnieje. Wybierz inną nazwę użytkownika.")
        name = form.name.data
        form.name.data = ''
        form.nick.data = ''
        form.password_hash.data = ''
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.htm",
        form=form,
        name=name,
        our_users=our_users)

@app.route('/uzytkownik/edytuj/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)
    edited = None
    if request.method == "POST":
        user = Users.query.filter_by(nick=form.nick.data).first()
        if user == user_to_update.nick:
            user=None
        if user is None:
            user_to_update.name = request.form['name']
            user_to_update.nick = request.form['nick']
            try:
                db.session.commit()
                flash("Zmieniono dane.")
                edited = "tak"
                title = "Zmieniono dane."
                return render_template("back_to_users.htm", title = title)
            except:
                flash("Wystąpił błąd, spróbuj ponownie.")
                return render_template("update.htm",
                                       form=form,
                                       user_to_update=user_to_update)
        else:
            # uwaga! to psuje, jeśli użytkownik nie zmieni nicku! coś jest źle!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! <-rozwiązanie: można usunąć możliwość zmiany nicku
            flash("Użytkownik o tym nicku już istnieje. Wybierz inną nazwę użytkownika.")
    else:
        return render_template("update.htm",
                               form=form,
                               user_to_update=user_to_update,
                               id=id)

@app.route('/uzytkownik/usun/<int:id>')
def delete(id):
    name = None
    deleted = None
    title = "Usunięto użytkownika."
    form = UserForm()
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("Usunięto użytkownika")
        deleted = "tak"
        our_users = Users.query.order_by(Users.date_added)
        return render_template("back_to_users.htm", title = title)
    except:
        flash("Wystąpił błąd, spróbuj ponownie.")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.htm", form=form, name=name, our_users=our_users)



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.htm'), 404

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()



# ssh 20_palonek@limba.wzks.uj.edu.pl -p 4016
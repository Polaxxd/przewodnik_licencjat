from flask import Flask
from flask import render_template, redirect
from flask import flash
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash

#from babel import Babel

app = Flask(__name__)
app.config['SECRET_KEY'] = "przewodnik_pola"
#Add database
db = SQLAlchemy()
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://20_palonek:polap1103@127.0.0.1/20_palonek'
# Initialize The Database
db.init_app(app)

# babel = Babel(app)
# @babel.localeselector
# def get_locale():
#     return 'pl'

# Create Model for Users
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
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


# Create Model for Quiz
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255))
    option4 = db.Column(db.String(255))
    correct_answer = db.Column(db.Integer, nullable=False)

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


################## FORMS #####################
# Create a Form Class to add and update users
class UserForm(FlaskForm):
    name = StringField("Imię", validators=[DataRequired()])
    nick = StringField("Nick", validators=[DataRequired()])
    password_hash = PasswordField('Hasło', validators=[DataRequired(), EqualTo('password_hash2', message="Hasła muszą być takie same!")])
    password_hash2 = PasswordField('Powtórz hasło', validators=[DataRequired()])
    submit = SubmitField("Zapisz")

# Create a Name Form Class
class NamerForm(FlaskForm):
    Nname = StringField("Imię", validators=[DataRequired()])
    submit = SubmitField("Prześlij")

# Create a Login Form
class LoginForm(FlaskForm):
    nick = StringField("Nick", validators=[DataRequired()])
    password = PasswordField("Hasło", validators=[DataRequired()])
    submit = SubmitField("Zaloguj")

# Create a Form Class to add quiz questions
class QuizForm(FlaskForm):
    question_text = StringField("Pytanie", validators=[DataRequired()])
    option1 = StringField("Odpowiedź 1", validators=[DataRequired()])
    option2 = StringField("Odpowiedź 2", validators=[DataRequired()])
    option3 = StringField("Odpowiedź 3")
    option4 = StringField("Odpowiedź 4")
    correct_answer = IntegerField("Prawidłowa odpowiedź", validators=[DataRequired()])
    submit = SubmitField("Zapisz")

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

@app.route('/logowanie', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(nick=form.nick.data).first()
        if user:
            # check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Zalogowano!")
                return redirect(url_for('dashboard'))
            else:
                flash("Błędne hasło!")
        else:
            flash("Brak użytkownika.")
    return render_template('login.htm', form=form)

@app.route('/wyloguj', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Wylogowano.")
    return redirect(url_for('login'))

@app.route('/panel_uzytkownika')
@login_required
def dashboard():
    return render_template('dashboard.htm')

@app.route('/uzytkownik', methods=['GET', 'POST'])
def name():
    Nname = None
    Nform = NamerForm()
    # Validate Form
    if Nform.validate_on_submit():
        Nname = Nform.Nname.data
        Nform.Nname.data = ''
        flash("Form Submitted Successfully!")


    return render_template("dashboard.htm",
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
        if user.nick == form.nick.data:
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

@app.route('/quiz/dodaj', methods=['GET', 'POST'])
def add_question():
    added = None
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(
            question_text=form.question_text.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            correct_answer=form.correct_answer.data
        )
        db.session.add(quiz)
        db.session.commit()
        flash("Dodano pytanie")
        added = "tak"

        form.question_text.data = ''
        form.option1.data = ''
        form.option2.data = ''
        form.option3.data = ''
        form.option4.data = ''
        form.correct_answer.data = ''

    my_questions = Quiz.query.order_by(Quiz.id.asc()).all()
    return render_template("quiz_adding.htm",
                           form=form,
                           added=added,
                           my_questions=my_questions)

@app.route('/quiz/edytuj/<int:id>', methods=['GET', 'POST'])
def update_question(id):
    form = QuizForm()
    question_to_update = Quiz.query.get_or_404(id)
    my_questions = Quiz.query.order_by(Quiz.id.asc()).all()
    edited = None
    if request.method == "POST":
        question_to_update.question_text = request.form['question_text']
        question_to_update.option1 = request.form['option1']
        question_to_update.option2 = request.form['option2']
        question_to_update.option3 = request.form['option3']
        question_to_update.option4 = request.form['option4']
        question_to_update.correct_answer = request.form['correct_answer']
        try:
            db.session.commit()
            flash("Zmieniono dane.")
            edited = "tak"
            return render_template("quiz_adding.htm",
                                   form=form,
                                   my_questions=my_questions,
                                   edited=edited
                                   )
        except:
            flash("Wystąpił błąd, spróbuj ponownie.")
            return render_template("quiz_update.htm",
                                   form=form,
                                   question_to_update=question_to_update,
                                   id=id)

    else:
        return render_template("quiz_update.htm",
                               form=form,
                               question_to_update=question_to_update,
                               id=id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.htm'), 404

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()



# ssh 20_palonek@limba.wzks.uj.edu.pl -p 4016
from flask import Flask
from flask import render_template, redirect
from flask import flash
from flask import request
from flask import url_for

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from forms import UserForm, NamerForm, LoginForm, QuizForm, QuestionForm, WordsForm, WordForm

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
    quiz_score = db.Column(db.Integer, default=0)

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

# Create Model for Words
class Words(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word_text = db.Column(db.String(200), nullable=False, unique=True)
    characters = db.Column(db.String(255))
    video = db.Column(db.String(200), default="no_video")

# Create Model for Scores
class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    type = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



@app.route('/')
def home():
    return render_template('home.htm')

@app.route('/kultura')
def kultura():
    return render_template('kultura.htm')

@app.route('/daktylografia')
def daktylografia():
    return render_template('daktylografia/daktylografia.htm')

@app.route('/daktylografia/teoria')
def daktylografia_teoria():
    return render_template('daktylografia/teoria.htm')

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
    return render_template('users/login.htm', form=form)

@app.route('/wyloguj', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Wylogowano.")
    return redirect(url_for('login'))

@app.route('/panel_uzytkownika')
@login_required
def dashboard():
    photo_scores = Scores.query.filter_by(user_id=current_user.id, type="photo").order_by(Scores.date_added)
    ps = None
    photo_user_points = 0
    photo_max_points = 0
    video_scores = Scores.query.filter_by(user_id=current_user.id, type="video").order_by(Scores.date_added)
    vs = None
    video_user_points = 0
    video_max_points = 0
    all_words = Words.query.order_by(Words.id)
    for photo_score in photo_scores:
        ps = "yes"
        photo_max_points += 1
        if photo_score.score == 1:
            photo_user_points += 1
    for video_score in video_scores:
        vs = "yes"
        video_max_points += 1
        if video_score.score == 1:
            video_user_points += 1
    return render_template('dashboard.htm',
                           photo_scores=photo_scores,
                           video_scores = video_scores,
                           all_words=all_words,
                           photo_user_points=photo_user_points,
                           photo_max_points=photo_max_points,
                           video_user_points = video_user_points,
                           video_max_points = video_max_points,
                           vs = vs,
                           ps = ps
                           )

@app.route('/uzytkownik/zarejestruj', methods=['GET', 'POST'])
def register():
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
    return render_template("users/register.htm",
                           form=form,
                           name=name)


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
    return render_template("users/add_user.htm",
                           form=form,
                           name=name,
                           our_users=our_users)

@app.route('/uzytkownik/edytuj/<int:id>', methods=['GET', 'POST'])
@login_required
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
                return render_template("users/back_to_users.htm", title = title)
            except:
                flash("Wystąpił błąd, spróbuj ponownie.")
                return render_template("users/update.htm",
                                       form=form,
                                       user_to_update=user_to_update)
        else:
            # uwaga! to psuje, jeśli użytkownik nie zmieni nicku! coś jest źle!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! <-rozwiązanie: można usunąć możliwość zmiany nicku
            flash("Użytkownik o tym nicku już istnieje. Wybierz inną nazwę użytkownika.")
    else:
        return render_template("users/update.htm",
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
        return render_template("users/back_to_users.htm", title = title)
    except:
        flash("Wystąpił błąd, spróbuj ponownie.")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("users/add_user.htm", form=form, name=name, our_users=our_users)

# @app.route('/quiz', methods=['GET', 'POST'])
# def quiz():
#     if request.method == 'POST':
#         questions = Quiz.query.all()
#         score = 0
#         for question in questions:
#             user_answer = int(request.form.get(f'question_{question.id}'))
#             question.user_answer = user_answer
#             if user_answer == question.correct_answer:
#                 score += 1
#         db.session.commit()
#         return render_template('quiz_result.html', score=score)
#     else:
#         questions = Quiz.query.all()
#         return render_template('quiz.html', questions=questions)

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
    return render_template("quiz/quiz_adding.htm",
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
            return render_template("quiz/quiz_adding.htm",
                                   form=form,
                                   my_questions=my_questions,
                                   edited=edited
                                   )
        except:
            flash("Wystąpił błąd, spróbuj ponownie.")
            return render_template("quiz/quiz_update.htm",
                                   form=form,
                                   question_to_update=question_to_update,
                                   id=id)

    else:
        return render_template("quiz/quiz_update.htm",
                               form=form,
                               question_to_update=question_to_update,
                               id=id)

# @app.route('/question/<int:id>', methods=['GET', 'POST'])
# @login_required
# def question(id):
#     form = QuestionForm()
#     q = Quiz.query.filter_by(id=id).first()
#     message_x = None
#     message_y = "nie"
#     if not q:
#         return redirect(url_for('score'))
#     form.options.choices = [('1', q.option1), ('2', q.option2), ('3', q.option3), ('4', q.option4)]
#     if form.validate_on_submit():
#         message_y = "tak"
#         option = form.options.data
#         if option == q.correct_answer:
#             message_x = "poprawna odpowiedź"
#             current_score = current_user.quiz_score
#             current_score += 10
#             current_user.quiz_score = current_score
#         else:
#             message_x = "niepoprawna odpowiedź"+ option + "," + str(q.correct_answer)
#         return redirect(url_for('question', id=(id+1)))
#     #form.options.choices = [('1', q.option1), ('2', q.option2), ('3', q.option3), ('4', q.option4)]
#     return render_template('question.htm', form=form, q=q, title='Question {}'.format(id), message_x=message_x, message_y=message_y)

@app.route('/pytanie/<int:id>', methods=['GET', 'POST'])
@login_required
def question(id):
    form = QuestionForm()
    q = Quiz.query.filter_by(id=id).first()
    #działa?
    if id == 1:
        if current_user.quiz_score > 0:
            return redirect(url_for('score'))
    if not q:
        return redirect(url_for('score'))
    if request.method == 'POST':
        option = request.form['options']
        if option == q.correct_answer:
            current_score = current_user.quiz_score
            current_score += 10
            current_user.quiz_score = current_score
            try:
                db.session.commit()
            except:
                flash("Wystąpił błąd, spróbuj ponownie.")
        return redirect(url_for('question', id=(id+1)))
    form.options.choices = [('1', q.option1), ('2', q.option2), ('3', q.option3), ('4', q.option4)]
    return render_template('quiz/question.htm', form=form, q=q, title='Question {}'.format(id))


@app.route('/wynik_quizu')
@login_required
def score():
    final_score = current_user.quiz_score
    return render_template('quiz/score.htm', title='Final Score', score=final_score)

@app.route('/quiz/odpowiedzi')
@login_required
def quiz_answers():
    my_questions = Quiz.query.order_by(Quiz.id.asc()).all()
    return render_template('quiz/quiz_answers.htm', my_questions=my_questions)

# @app.route('/pytanie/<int:id>', methods=['GET', 'POST'])
# def question2(id):
#     message_z = "nic"
#     current_score = 0
#     form = Question2Form()
#     q = Quiz.query.filter_by(id=id).first()
#     if form.validate_on_submit():
#         message_z = "przeszło walidację"
#         q = Quiz.query.filter_by(id=id).first()
#         if q is None:
#             return redirect(url_for('score'))
#         else:
#             message_z = "doszło do else"
#             if str(form.user_answer.data) == str(q.correct_answer):
#                 message_z = "odpowiedź poprawna"
#                 current_score = current_user.quiz_score
#                 current_score = current_score+10
#                 current_user.quiz_score = current_score
#                 try:
#                     db.session.commit()
#                 except:
#                     flash("Wystąpił błąd, spróbuj ponownie.")
#             else:
#                 message_z = "odpowiedź niepoprawna"
#         form.user_answer.data = ''
#         return redirect(url_for('question2', id=(id + 1), message_z=message_z, cs = current_score, cus = current_user.quiz_score))
#
#
#     return render_template("question2.htm",
#         form=form,
#         q=q, message_z=message_z)

@app.route('/slowa/dodaj', methods=['GET', 'POST'])
@login_required
def add_word():
    added = None
    form = WordsForm()
    if form.validate_on_submit():
        word = Words(
            word_text=form.word_text.data,
            characters=form.characters.data,
            video=form.video.data,
        )
        db.session.add(word)
        db.session.commit()
        flash("Dodano wyraz")
        added = "tak"

        form.word_text.data = ''
        form.characters.data = ''
        form.video.data = ''

    my_words = Words.query.order_by(Words.id.asc()).all()
    return render_template("words/words_adding.htm",
                           form=form,
                           added=added,
                           my_words=my_words)

@app.route('/slowa/edytuj/<int:id>', methods=['GET', 'POST'])
@login_required
def update_word(id):
    form = WordsForm()
    word_to_update = Words.query.get_or_404(id)
    my_words = Words.query.order_by(Words.id.asc()).all()
    edited = None
    if request.method == "POST":
        word_to_update.word_text = request.form['word_text']
        word_to_update.characters = request.form['characters']
        word_to_update.video = request.form['video']
        try:
            db.session.commit()
            flash("Zmieniono dane.")
            edited = "tak"
            return render_template("words/words_adding.htm",
                                   form=form,
                                   my_words=my_words,
                                   edited=edited
                                   )
        except:
            flash("Wystąpił błąd, spróbuj ponownie.")
            return render_template("words/words_update.htm",
                                   form=form,
                                   word_to_update=word_to_update,
                                   id=id)

    else:
        return render_template("words/words_update.htm",
                               form=form,
                               word_to_update=word_to_update,
                               id=id)

@app.route('/zdjecia/<int:id>', methods=['GET', 'POST'])
@login_required
def word_photos(id):
    form = WordForm()
    w = Words.query.filter_by(id=id).first()
    if not w:
        return redirect(url_for('words_end'))
    else:
        chars = w.characters
        chars_list = chars.split(" ")
    if request.method == 'POST':
        if str(form.user_answer.data) == str(w.word_text):
            score1=Scores(
                word_id = id,
                user_id = current_user.id,
                type = "photo",
                score = 1
            )
            db.session.add(score1)
            db.session.commit()
            flash("Poprawnie!")
        else:
            score1 = Scores(
                word_id=id,
                user_id=current_user.id,
                type="photo",
                score=0
            )
            db.session.add(score1)
            db.session.commit()
            flash("Niepoprawnie.")
        return redirect(url_for('word_photos', id=(id + 1)))
    return render_template('words/word_photo.htm', form=form, w=w, chars_list=chars_list)

@app.route('/zdjecia/start')
@login_required
def word_photos_start():
    s = Scores.query.filter_by(user_id=current_user.id, type="photo").order_by(Scores.date_added.desc()).first()
    if s is None:
        new_id = 1
    else:
        last_id = s.word_id
        new_id = last_id+1
    return render_template('words/words_photos_start.htm', new_id=new_id)

@app.route('/nagrania/<int:id>', methods=['GET', 'POST'])
@login_required
def word_videos(id):
    form = WordForm()
    w = Words.query.filter_by(id=id).first()
    if not w:
        return redirect(url_for('words_end'))
    else:
        video_file = w.video
    if request.method == 'POST':
        if str(form.user_answer.data) == str(w.word_text):
            score1=Scores(
                word_id = id,
                user_id = current_user.id,
                type = "video",
                score = 1
            )
            db.session.add(score1)
            db.session.commit()
        else:
            score1 = Scores(
                word_id=id,
                user_id=current_user.id,
                type="video",
                score=0
            )
            db.session.add(score1)
            db.session.commit()
        return redirect(url_for('word_videos', id=(id + 1)))
    return render_template('words/word_video.htm', form=form, w=w, video_file=video_file)

@app.route('/nagrania/start')
@login_required
def word_videos_start():
    s = Scores.query.filter_by(user_id=current_user.id, type="video").order_by(Scores.date_added.desc()).first()
    if s is None:
        new_id = 1
    else:
        last_id = s.word_id
        new_id = last_id + 1
    return render_template('words/words_videos_start.htm', new_id=new_id)


@app.route('/slowa_koniec', methods=['GET', 'POST'])
@login_required
def words_end():
    return render_template('words/words_end.htm')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.htm'), 404

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()



# ssh 20_palonek@limba.wzks.uj.edu.pl -p 4016
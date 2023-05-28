from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, RadioField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length


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

# Create a Form Class for quiz questions
class QuestionForm(FlaskForm):
    options = RadioField('Options: ', validators=[DataRequired()], default=1, coerce=str)
    submit = SubmitField('Dalej')

# Create a 2nd Form Class for quiz questions
class Question2Form(FlaskForm):
    user_answer = IntegerField("Twoja odpowiedź", validators=[DataRequired()])
    submit = SubmitField('Dalej')

# Create a Form Class for words
class WordsForm(FlaskForm):
    word_text = StringField("Słowo", validators=[DataRequired()])
    characters = StringField("Znaki", validators=[DataRequired()])
    video = StringField("Nazwa filmu")
    submit = SubmitField("Zapisz")

# Create a Form Class for word guessing
class WordForm(FlaskForm):
    user_answer = StringField("Twoja odpowiedź", validators=[DataRequired()])
    submit = SubmitField('Dalej')
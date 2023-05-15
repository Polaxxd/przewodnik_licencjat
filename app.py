from flask import Flask
from flask import render_template
from flask import flash
from flask_wtf import FlaskForm
from datetime import datetime

app = Flask(__name__)


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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.htm'), 404


if __name__ == '__main__':
    app.run()



# ssh 20_palonek@limba.wzks.uj.edu.pl -p 4016
from flask import (Flask, request, redirect, url_for, make_response, render_template, flash)
from ES_data import ES_Data
from config import Config
from login_form import LoginForm
import requests

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
es = ES_Data()


@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'Toan'}
    return render_template("index.html", title='Index', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            login_form.username.data, login_form.remember_me.data))
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=login_form)


@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html', title='Search Form')


@app.route("/load", methods=['GET', 'POST'])
def load():
    nb_hits, result_data = es.search()
    response = make_response(render_template("table.html", nb_hits=nb_hits, data=result_data))
    return response



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)

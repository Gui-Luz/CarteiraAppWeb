from flask import Flask, render_template, url_for, session, redirect, request, flash
import configparser
from core.core import jwt_check
import requests

config_file = configparser.ConfigParser()
config_file.read('config.ini')

HOST = config_file['ENDPOINTS']['host']
USER_ENDPOINT = config_file['ENDPOINTS']['user']
AUTH_ENDPOINT = config_file['ENDPOINTS']['auth_user']
PORTFOLIO_ENDPOINT = config_file['ENDPOINTS']['portfolios']

DEBUG = config_file['ENV']['debug']

app_name = config_file['APP']['name']
app = Flask(__name__)
app.secret_key = config_file['APP']['secret_key']


@app.route('/')
def index():
    if jwt_check():
        return redirect(url_for('portfolio'))
    else:
        nav = ['disabled', 'disabled', '', '/', 'LOGIN']
        return render_template('login.html', nome_do_app=app_name, nav=nav)


@app.route('/portfolio')
def portfolio():
    if jwt_check():
        r_url = f"http://{HOST}{PORTFOLIO_ENDPOINT}?user_id={session['user_id']}"
        r = requests.get(r_url).json()
        if r['Code'] == 200:
            portfolio_totals = (r['Data']['Portfolio totals'])
            portfolio_details = (r['Data']['Portfolio details'])
            nav = ['active', '', session['username'], '/logout', 'LOGOUT']
            return render_template('portfolio.html', nome_do_app=app_name, nav=nav, portfolio_details=portfolio_details,
                                   portfolio_totals=portfolio_totals)
        else:
            if r['Message'] == 'Portfolio not found':
                nav = ['active', '', session['username'], '/logout', 'LOGOUT']
                return render_template('new_portfolio.html', nome_do_app=app_name, nav=nav)
            else:
                return f"{r['Message']}"
    else:
        nav = ['disabled', 'disabled', '', '/', 'LOGIN']
        return render_template('login.html', nome_do_app=app_name, nav=nav)


@app.route('/history')
def history():
    if jwt_check():
        return f"Bem vindo ao histórico {session['username']}, {session['jwt']}"
    else:
        nav = ['disabled', 'disabled', '', '/', 'LOGIN']
        return render_template('login.html', nome_do_app=app_name, nav=nav)


@app.route('/logout')
def logout():
    session['username'] = None
    session['jwt'] =None
    return redirect(url_for('index'))


@app.route('/authenticate', methods=['POST', ])
def authenticate():
    username = request.form['username']
    password = request.form['password']
    r_url = f'http://{HOST}{AUTH_ENDPOINT}?username={username}&password={password}'
    r = requests.get(r_url).json()
    if r['Code'] == 200:
        session['jwt'] = r['Data']['Jwt']
        session['username'] = r['Data']['Username']
        session['user_id'] = r['Data']['Id']
        return redirect(url_for('portfolio'))
    else:
        flash(f'Usuário não encontrado.', 'danger')
        return redirect(url_for('index'))


@app.route('/sign_up', methods=['POST', ])
def sign_up():
    signup_name = request.form['name']
    signup_user_name = request.form['user_name']
    signup_password = request.form['password']
    signup_email = request.form['email']
    r_url = f'http://{HOST}{USER_ENDPOINT}?username={signup_user_name}&email={signup_email}&password={signup_password}'
    r = requests.post(r_url).json()
    if r['Code'] == 200:
        flash(f'Usuário cadastrado com sucesso.', 'success')
        return redirect(url_for('index'))
    else:
        flash(f'Erro ao cadastrar usuário.', 'danger')
        return redirect(url_for('index'))


@app.route('/add_stocks', methods=['POST',])
def add_stocks():
    pass


if __name__ == '__main__':
    app.run(debug=bool(DEBUG), port=8000)


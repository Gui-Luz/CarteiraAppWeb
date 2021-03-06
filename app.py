import os
from flask import Flask, render_template, url_for, session, redirect, request, flash
import configparser
from core.core import jwt_check
import requests
import ast

config_file = configparser.ConfigParser()
config_file.read(os.path.dirname(__file__) + '/config.ini')

# Endpoints
HOST = config_file['ENDPOINTS']['host']
USER_ENDPOINT = config_file['ENDPOINTS']['user']
AUTH_ENDPOINT = config_file['ENDPOINTS']['auth_user']
PORTFOLIO_ENDPOINT = config_file['ENDPOINTS']['portfolios']
OPEN_OPERATION = config_file['ENDPOINTS']['open_operations']
RECORDS = config_file['ENDPOINTS']['records']
UPDATE_OPEN_STOCK = config_file['ENDPOINTS']['update_open_stock']
UPDATE_CLOSED_STOCK = config_file['ENDPOINTS']['update_closed_stock']

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
                nav = ['active', 'disabled', session['username'], '/logout', 'LOGOUT']
                return render_template('new_portfolio.html', nome_do_app=app_name, nav=nav)
            else:
                return f"{r['Message']}"
    else:
        nav = ['disabled', 'disabled', '', '/', 'LOGIN']
        return render_template('login.html', nome_do_app=app_name, nav=nav)


@app.route('/history')
def history():
    if jwt_check():
        r_url = f"http://{HOST}{RECORDS}?user_id={session['user_id']}"
        r = requests.get(r_url).json()
        if r['Code'] == 200:
            stocks = r['Data']['Stocks']
            totals = r['Data']['Totals']
            nav = ['', 'active', session['username'], '/logout', 'LOGOUT']
            return render_template('records.html', nome_do_app=app_name, nav=nav, stocks=stocks, totals=totals)
    else:
        nav = ['disabled', 'disabled', '', '/', 'LOGIN']
        return render_template('login.html', nome_do_app=app_name, nav=nav)


@app.route('/logout')
def logout():
    session['username'] = None
    session['jwt'] = None
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
        session['name'] = r['Data']['Name']
        session['email'] = r['Data']['Email']
        return redirect(url_for('portfolio'))
    else:
        flash(f'Usu??rio n??o encontrado.', 'danger')
        return redirect(url_for('index'))


@app.route('/sign_up', methods=['POST', ])
def sign_up():
    signup_name = request.form['name']
    signup_user_name = request.form['user_name']
    signup_password = request.form['password']
    signup_email = request.form['email']
    r_url = f'http://{HOST}{USER_ENDPOINT}?name={signup_name}&username={signup_user_name}&email={signup_email}&password={signup_password}'
    r = requests.post(r_url).json()
    if r['Code'] == 200:
        flash(f'Usu??rio cadastrado com sucesso.', 'success')
        return redirect(url_for('index'))
    else:
        flash(f'Erro ao cadastrar usu??rio.', 'danger')
        return redirect(url_for('index'))


@app.route('/add_stocks', methods=['POST', ])
def add_stocks():
    stock = str(request.form['stock'].upper())
    price = float(request.form['price'].replace(',', '.'))
    quantity = int(request.form['quantity'])
    date = (request.form['date'].replace('/', '-'))
    portfolio = str(request.form['portfolio'])
    r_url = f"http://{HOST}{OPEN_OPERATION}?user_id={session['user_id']}&stock={stock}&price={price}&quantity={quantity}&date={date}&portfolio={portfolio} "
    r = requests.post(r_url).json()
    if r['Code'] == 200:
        flash(f'A????o adicionada com sucesso.', 'success')
        return redirect(url_for('index'))
    else:
        flash(f"{r['Message']}.", 'danger')
        return redirect(url_for('index'))


@app.route('/sell_stocks', methods=['POST', ])
def sell_stocks():
    stock = request.args['stock']
    portfolio = request.args['portfolio']
    price = float(request.form['price'].replace(',', '.'))
    date = (request.form['date'].replace('/', '-'))
    quantity = int(request.form['quantity'])

    r_url = f"http://{HOST}{OPEN_OPERATION}?user_id={session['user_id']}&stock={stock}&sold_price={price}&quantity={quantity}&sold_date={date}&portfolio={portfolio} "
    r = requests.delete(r_url).json()
    if r['Code'] == 200:
        flash(f'A????o vendida com sucesso.', 'success')
        return redirect(url_for('index'))
    else:
        flash(f"{r['Message']}.", 'danger')
        return redirect(url_for('index'))


@app.route('/update_stocks', methods=['POST'])
def update_stocks():
    if request.args['status'] == 'Closed':
        id_list = request.args['id_list']
        stock = request.args['stock']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'].replace(',', '.'))
        date = (request.form['date'].replace('/', '-'))
        sold_price = float(request.form['sold_price'].replace(',', '.'))
        sold_date = (request.form['sold_date'].replace('/', '-'))
        portfolio = request.form['portfolio']
        print(portfolio)
        r_url = f"http://{HOST}{UPDATE_CLOSED_STOCK}?user_id={session['user_id']}&stock={stock}&price={price}&date={date}&sold_price={sold_price}&sold_date={sold_date}&portfolio={portfolio}&id_list={id_list}"
        r = requests.put(r_url).json()
        if r['Code'] == 200:
            flash(f'A????o editada com sucesso.', 'success')
            return redirect(url_for('index'))
        else:
            flash(f"{r['Message']}.", 'danger')
            return redirect(url_for('index'))

    elif request.args['status'] == 'Open':
        id_list = request.args['id_list']
        stock = request.args['stock']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'].replace(',', '.'))
        date = (request.form['date'].replace('/', '-'))
        portfolio = request.form['portfolio']
        r_url = f"http://{HOST}{UPDATE_OPEN_STOCK}?user_id={session['user_id']}&stock={stock}&price={price}&date={date}&portfolio={portfolio}&id_list={id_list}"
        r = requests.put(r_url).json()
        if r['Code'] == 200:
            flash(f'A????o editada com sucesso.', 'success')
            return redirect(url_for('index'))
        else:
            flash(f"Houve erro na edi????o.", 'danger')
            return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=bool(DEBUG), port=8000)

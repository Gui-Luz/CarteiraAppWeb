from flask import session
import jwt
import configparser

config_file = configparser.ConfigParser()
config_file.read('config.ini')


def jwt_check():
    try:
        if session['jwt'] and session['username'] and session['user_id']:
            jwt_decode = jwt.decode(session['jwt'], config_file['JWT']['salt'], algorithms=["HS256"])
            if jwt_decode == {'id': session['user_id'], 'username': session['username']}:
                return True
            else:
                return False
        else:
            return False

    except KeyError:
        return False

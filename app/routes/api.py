from flask import Blueprint, request, jsonify, session
from app.models import User
from app.db import get_db
import sys

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/users', methods=['POST'])
def signup():
    # capture data sent by POST request. returns a dictionary
    data = request.get_json()
    # print(data)
    db = get_db()

    try:
        newUser = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )

        # save in database
        db.add(newUser)
        db.commit()

    except:
        # insert failed, so send error to front end
        print(sys.exc_info()[0])

        # insert failed, so rollback (to avoid crashing production app) and send error to front end
        db.rollback()
        return jsonify(message='Signup failed'), 500

    # clear any existing session data.  session is possible because we defined secret key in app/__init__.py
    session.clear()
    session['user_id'] = newUser.id
    session['loggedIn'] = True

    return jsonify(id=newUser.id)


@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()

    try:
        user = db.query(User).filter(User.email == data['email']).one()
    except:
        print(sys.exc_info()[0])

    if user.verify_password(data['password']) == False:
        return jsonify(message='Incorrect credentials'), 400

    # if email and password pass the checks, create session and log in user
    session.clear()
    session['user_id'] = user.id
    session['loggedIn'] = True

    return jsonify(id=user.id)


@bp.route('/users/logout', methods=['POST'])
def logout():
    # remove session variables
    session.clear()
    return '', 204

from flask import Flask, request, jsonify, make_response
from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from harmony import db, app
from harmony.models.user import UserAccount, UserSwipes


def token_required(f):
    @wraps(f)
    def decorator(self):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = UserAccount.query.filter_by(
                public_id=data['public_id']).first()

        except:
            return jsonify({'message': 'token is invalid'})

        return f(self, current_user)

    return decorator


class SignUp(Resource):
    def post(self):
        data = request.get_json()

        hashed_password = generate_password_hash(data['password'], method='sha256')
        user = UserAccount.query.filter_by(email=data['email']).first()
        if user:
            return make_response(jsonify({'success': False, 'error': "User already exists"}), 400)
        new_user = UserAccount(public_id=str(uuid.uuid4()), f_name=data['f_name'], email=data['email'],
                               password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            swipe_list = UserSwipes(user_id=new_user.id)
            db.session.add(swipe_list)
            db.session.commit()
            print(new_user)
            token = jwt.encode(
                {'public_id': new_user.public_id, 'exp': datetime.datetime.utcnow(
                ) + datetime.timedelta(minutes=300)},
                app.config['SECRET_KEY'])

            return make_response(
                jsonify({'token': token.encode().decode('UTF-8'), 'public_user_id': new_user.public_id}), 200)
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return make_response(jsonify({'msg': "could not signup", 'error': error}), 401)


class Login(Resource):
    def get(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

        user = UserAccount.query.filter_by(email=auth.username).first()

        if check_password_hash(user.password, auth.password):
            token = jwt.encode(
                {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=300)},
                app.config['SECRET_KEY'])
            return make_response(jsonify({'token': token.encode().decode('UTF-8'), 'public_user_id': user.public_id}),
                                 200)

        return make_response(jsonify({'messages': 'could not verify'}), 401)

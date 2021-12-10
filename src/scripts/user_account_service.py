from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from models import *
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError
from http import HTTPStatus

app = Flask(__name__)  # creating the Flask class object
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.sqlite3'
app.config['SECRET_KEY'] = "secret key"


@app.before_first_request
def setup_db():
    db.init_app(app)
    db.create_all()


@app.route('/')  # decorator drfines the
def home():
    return "hello, this is our first flask website";


@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json

    user = User(name=data.get('name'),
                hashed_passwd=data.get('hashed_passwd'),
                national_id=data.get('national_id'),

                role=data.get('role'))

    try:
        db.session.add(user)
        db.session.commit()
        return {'message': 'Success'}, HTTPStatus.CREATED

    except IntegrityError as e:
        if 'UNIQUE' in str(e):
            return {'message': 'Error: national id already exists'}, HTTPStatus.CONFLICT
        else:
            return {'message': 'Error: bad request error'}, HTTPStatus.BAD_REQUEST


@app.route('/create_admin', methods=['POST'])
def create_user():
    data = request.json

    user = User(username=data.get('username'),
                hashed_passwd=data.get('hashed_passwd'),

                role=data.get('role'))

    try:
        db.session.add(user)
        db.session.commit()
        return {'message': 'Success'}, HTTPStatus.CREATED

    except IntegrityError as e:
        if 'UNIQUE' in str(e):
            return {'message': 'Error: username already exists'}, HTTPStatus.CONFLICT
        else:
            return {'message': 'Error: bad request error'}, HTTPStatus.BAD_REQUEST


@app.route('/user/<national_id>')
def get_user(national_id):
    user = User.query.get(national_id)

    if user is None:
        return {'message': 'Error: No user found'}, HTTPStatus.NOT_FOUND
    else:
        return {'message': 'Success', 'user': user.to_dict()}, HTTPStatus.OK


@app.route('/admin/<username>')
def get_admin(username):
    user = Admin.query.get(username)

    if user is None:
        return {'message': 'Error: No user found'}, HTTPStatus.NOT_FOUND
    else:
        return {'message': 'Success', 'user': user.to_dict()}, HTTPStatus.OK


@app.route('/show_patients', methods=['GET'])
def all_patient():
    return jsonify([u.to_dict() for u in User.query.filter_by(role="patient").all()])


@app.route('/show_doctors', methods=['GET'])
def all_doctors():
    return jsonify([u.to_dict() for u in User.query.filter_by(role="doctor").all()])


if __name__ == '__main__':
    app.run(debug=True)

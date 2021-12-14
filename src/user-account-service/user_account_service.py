from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from models import *
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError
from http import HTTPStatus

app = Flask(__name__)  # creating the Flask class object
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.sqlite3'
app.config['SECRET_KEY'] = "secret key"
print(__name__)


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

        return jsonify({'message': 'Success'}), HTTPStatus.CREATED

    except IntegrityError as e:
        if 'UNIQUE' in str(e):
            return jsonify({'message': 'Error: national id already exists'}), HTTPStatus.CONFLICT
        else:
            return jsonify({'message': 'Error: bad request error'}), HTTPStatus.BAD_REQUEST


@app.route('/create_admin', methods=['POST'])
def create_admin():
    data = request.json

    user = Admin(username=data.get('username'),
                 hashed_passwd=data.get('hashed_passwd')
                 )

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Success'}), HTTPStatus.CREATED

    except IntegrityError as e:
        if 'UNIQUE' in str(e):
            return jsonify({'message': 'Error: username already exists'}), HTTPStatus.CONFLICT
        else:
            return jsonify({'message': 'Error: bad request error'}), HTTPStatus.BAD_REQUEST


@app.route('/user/<national_id>')
def get_user(national_id):
    user = User.query.get(national_id)

    if user is None:
        return jsonify({'message': 'Error: No user found'}), HTTPStatus.NOT_FOUND
    else:
        return jsonify({'message': 'Success', 'user': user.to_dict()}), HTTPStatus.OK


@app.route("/user_profile")
def get_user_profile():

    username = list(request.args.to_dict(flat=False).keys())[0]
    user = User.query.get(username)
    your_keys = ['name', "role", 'national_id']
    dict_you_want = { your_key: user.to_dict()[your_key] for your_key in your_keys }

    return jsonify({'message': 'Success', 'user': dict_you_want}), HTTPStatus.OK

@app.route("/admin_profile")
def get_admin_profile():

    username = list(request.args.to_dict(flat=False).keys())[0]
    user = Admin.query.get(username)
    your_keys = ['username']
    dict_you_want = { your_key: user.to_dict()[your_key] for your_key in your_keys }

    return jsonify({'message': 'Success', 'user': dict_you_want}), HTTPStatus.OK



@app.route('/admin/<username>')
def get_admin(username):
    user = Admin.query.get(username)

    if user is None:
        return jsonify({'message': 'Error: No user found'}), HTTPStatus.NOT_FOUND
    else:
        return jsonify({'message': 'Success', 'user': user.to_dict()}), HTTPStatus.OK


@app.route('/show_patients/', methods=['GET'])
def all_patients():
    username = list(request.args.to_dict(flat=False).keys())[0]
    print("show patien", username)
    admin = Admin.query.get(username)
    if admin is None:
        return jsonify({'message': 'Error: you are not admin'}), HTTPStatus.NOT_FOUND
    temp_list = [u.to_dict() for u in User.query.filter_by(role="patient").all()]
    return_list = []
    your_keys = ['name', "role", 'national_id']
    for u in temp_list:
        dict_you_want = { your_key: u[your_key] for your_key in your_keys }
        return_list.append(dict_you_want)


    return jsonify(return_list)


@app.route('/show_doctors/', methods=['GET'])
def all_doctors():
    username = list(request.args.to_dict(flat=False).keys())[0]

    admin = Admin.query.get(username)
    if admin is None:
        return jsonify({'message': 'Error: you are not admin'}), HTTPStatus.NOT_FOUND
    temp_list = [u.to_dict() for u in User.query.filter_by(role="doctor").all()]
    return_list = []
    your_keys = ['name', "role", 'national_id']
    for u in temp_list:
        dict_you_want = { your_key: u[your_key] for your_key in your_keys }
        return_list.append(dict_you_want)


    return jsonify(return_list)


if __name__ == '__main__':
    app.run(debug=True)

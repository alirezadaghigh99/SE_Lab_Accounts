from datetime import date

from flask import Flask, request, g, session
from sqlalchemy import func

from models import *
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError
from http import HTTPStatus
from flask_migrate import Migrate

app = Flask(__name__)  # creating the Flask class object
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.sqlite3'
app.config['SECRET_KEY'] = "secret key"
db.init_app(app)
Migrate(app, db)


@app.before_first_request
def setup_db():
    db.init_app(app)
    db.create_all()


@app.route('/')  # decorator drfines the
def home():
    return "hello, this is our first flask website";


@app.route('/create_user/<role>', methods=['POST'])
def create_user(role):
    data = request.json
    if role == 'doctor':
        user = Doctor(name=data.get('name'),
                    hashed_passwd=data.get('hashed_passwd'),
                    national_id=data.get('national_id'))

    else:
        user = Patient(name=data.get('name'),
                    hashed_passwd=data.get('hashed_passwd'),
                    national_id=data.get('national_id'))

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


@app.route('/user/<role>/<national_id>')
def get_user(role, national_id):
    if role == "doctor":
        user = Doctor.query.filter_by(national_id=national_id).first()
    else:
        user = Patient.query.filter_by(national_id=national_id).first()

    if user is None:
        return jsonify({'message': 'Error: No user found'}), HTTPStatus.NOT_FOUND
    else:
        return jsonify({'message': 'Success', 'user': user.to_dict()}), HTTPStatus.OK


@app.route("/user_profile")
def get_user_profile():
    data = request.args.to_dict(flat=False)
    username = data["username"][0]
    role = data["role"][0]
    print(username, role)
    if role == "doctor":
        user = Doctor.query.filter_by(national_id=username).first()
    else:
        user = Patient.query.filter_by(national_id=username).first()

    your_keys = ['name', 'national_id']
    dict_you_want = {your_key: user.to_dict()[your_key] for your_key in your_keys}
    dict_you_want["role"] = role
    return jsonify({'message': 'Success', 'user': dict_you_want}), HTTPStatus.OK


@app.route("/admin_profile")
def get_admin_profile():
    username = list(request.args.to_dict(flat=False).keys())[0]
    user = Admin.query.get(username)
    your_keys = ['username']
    dict_you_want = {your_key: user.to_dict()[your_key] for your_key in your_keys}

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
    admin = Admin.query.get(username)
    if admin is None:
        return jsonify({'message': 'Error: you are not admin'}), HTTPStatus.NOT_FOUND
    temp_list = [u.to_dict() for u in Patient.query.all()]
    return_list = []
    your_keys = ['name', 'national_id']
    for u in temp_list:
        dict_you_want = {your_key: u[your_key] for your_key in your_keys}
        return_list.append(dict_you_want)

    return jsonify(return_list)


@app.route('/show_doctors/', methods=['GET'])
def all_doctors():
    username = list(request.args.to_dict(flat=False).keys())[0]

    admin = Admin.query.get(username)
    if admin is None:
        return jsonify({'message': 'Error: you are not admin'}), HTTPStatus.NOT_FOUND
    temp_list = [u.to_dict() for u in Doctor.query.all()]
    return_list = []
    your_keys = ['name', 'national_id']
    for u in temp_list:
        dict_you_want = {your_key: u[your_key] for your_key in your_keys}
        return_list.append(dict_you_want)

    return jsonify(return_list)


@app.route('/patients/stats', methods=['GET'])
def patients_stats():
    query = Patient.query
    try:
        day = int(request.args["day"])
        month = int(request.args["month"])
        year = int(request.args["year"])
        date_obj = date(year, month, day)
    except:
        return jsonify({"message": "Bad request"}), HTTPStatus.BAD_REQUEST
    query = query.filter(func.DATE(Patient.timestamp) == date_obj)
    return jsonify([patient.to_dict() for patient in query.all()])


@app.route('/doctors/stats', methods=['GET'])
def doctors_stats():
    query = Doctor.query
    try:
        day = int(request.args["day"])
        month = int(request.args["month"])
        year = int(request.args["year"])
        date_obj = date(year, month, day)
    except:
        return jsonify({"message": "Bad request"}), HTTPStatus.BAD_REQUEST
    query = query.filter(func.DATE(Doctor.timestamp) == date_obj)
    return jsonify([doctor.to_dict() for doctor in query.all()])


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)

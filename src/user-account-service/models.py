from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    hashed_passwd = db.Column(db.Text, nullable=False)
    national_id = db.Column(db.String(15), unique=True)
    role = db.Column(db.String(20))

    def to_dict(self):
        vals = vars(self)
        return {attr: vals[attr] for attr in vals if 'instance_state' not in attr}


class Admin(db.Model):
    username = db.Column(db.String(15), primary_key=True)
    hashed_passwd = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        vals = vars(self)
        return {attr: vals[attr] for attr in vals if 'instance_state' not in attr}

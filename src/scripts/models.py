from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    name = db.Column(db.String(15))
    hashed_passwd = db.Column(db.Text, nullable=False)
    national_id = db.Column(db.String(15), primary_key=True)
    role = db.Column(db.String(20))

    def to_dict(self):
        vals = vars(self)
        return {attr: vals[attr] for attr in vals if 'instance_state' not in attr}


class Admin(db.Model):
    username = db.Column(db.String(15), primary_key=True)
    hashed_passwd = db.Column(db.Text, nullable=False)

    def to_dict(self):
        vals = vars(self)
        return {attr: vals[attr] for attr in vals if 'instance_state' not in attr}

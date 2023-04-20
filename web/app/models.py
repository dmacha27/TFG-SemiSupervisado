from sqlalchemy import func

from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True)
    name = db.Column(db.String(10))
    password = db.Column(db.String(20))
    last_login = db.Column(db.DateTime)
    datasets = db.relationship('Dataset')


class Dataset(db.Model):
    __tablename__ = "Datasets"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    complete_path = db.Column(db.String(150))
    date = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    def to_list(self):
        return [self.filename, self.complete_path, self.date.strftime("%Y-%m-%d %H:%M:%S")]

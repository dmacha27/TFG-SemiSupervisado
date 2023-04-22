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
    runs = db.relationship('Run')


class Dataset(db.Model):
    __tablename__ = "Datasets"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), unique=True)
    date = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    def to_list(self):
        return [self.filename, self.date.strftime("%Y-%m-%d %H:%M:%S")]


class Run(db.Model):
    __tablename__ = "Runs"

    id = db.Column(db.Integer, primary_key=True)
    algorithm = db.Column(db.String(50))
    filename = db.Column(db.String(50))
    date = db.Column(db.DateTime, default=func.now())
    cx = db.Column(db.String(20))
    cy = db.Column(db.String(20))
    jsonfile = db.Column(db.String(50), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    def to_list(self):
        return [self.id, self.algorithm, self.filename, self.date.strftime("%Y-%m-%d %H:%M:%S"), self.cx, self.cy, self.jsonfile]

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default =func.now())
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'))

class Dates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checkin = db.Column(db.DateTime(timezone=True))
    checkout = db.Column(db.DateTime(timezone=True))
    guests = db.Column(db.String(10000))
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    notes = db.relationship('Dates')
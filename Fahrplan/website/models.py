from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    posts = db.relationship('Post', backref='user', passive_deletes=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # start = db.Column(db.Text, nullable=False)
    # ziel = db.Column(db.Text, nullable=False)
    # abfahrt = db.Column(db.DateTime, nullable=False)
    # ankunft = db.Column(db.DateTime, nullable=False)
    # zug = db.Column(db.Text, nullable=False)
    # preis = db.Column(db.Number, nullable=False)
    # bordpersonal = db.Column(db.Text)


    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)

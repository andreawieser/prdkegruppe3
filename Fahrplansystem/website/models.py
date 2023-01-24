from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask import json


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    admin = db.Column(db.String(150))
    posts = db.relationship('Post', backref='user', passive_deletes=True)

    def get_username(self):
        return self.username

    def get_admin(self):
        return self.admin


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Start und Endbahnhof
    start = db.Column(db.String, nullable=False)
    ziel = db.Column(db.String, nullable=False)
    # startBhf = db.Column(db.String, nullable=False)
    # endBhf = db.Column(db.String, nullable=False)


    zug = db.Column(db.String, nullable=False)
    # Zug = db.Column(db.String, nullable=False)
   
    bordpersonal = db.Column(db.String, nullable=False)
    preis = db.Column(db.Float, nullable=False)
    # Preis = db.Column(db.Float, nullable=False)
    
    datum = db.Column(db.String, nullable=False)
    # Datum = db.Column(db.String, nullable=False)
    
    # Abfahrtszeit und Ankunftszeit
    uhrzeit = db.Column(db.String, nullable=False)
    ankunft = db.Column(db.String, nullable=False)
    # Abfahrt = db.Column(db.String, nullable=False)
    # Ankunft = db.Column(db.String, nullable=False)
    strecken = db.Column(db.String, nullable=False)


    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



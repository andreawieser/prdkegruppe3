from . import db
from flask_login import UserMixin


# SQLAlchemy allows to represent the database structure as classes (called models)
# UserMixin makes authentication with flask_login a lot easier
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # 60 characters for password because of the hashing algorithm I used
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    # defines how an object is printed out
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Zug(db.Model):
    __tablename__ = 'zuege'
    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.String(120), unique=True, nullable=False)
    # backref allows for e.g. w.zug (when w = instance of Waggon)
    waggons = db.relationship("Waggon", backref="train")


# I chose single table inheritance because of supposedly better performance
class Waggon(db.Model):
    __tablename__ = 'waggons'
    id = db.Column(db.Integer, primary_key=True)
    fg_nummer = db.Column(db.String(120), unique=True, nullable=False)
    spurweite = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20))
    in_verwendung = db.Column(db.Boolean, nullable=False, default=False)
    zug = db.Column(db.Integer, db.ForeignKey("zuege.id"))

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "waggon",
    }


class Triebwagen(Waggon, db.Model):
    __tablename__ = 'triebwaegen'
    max_zugkraft = db.Column(db.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "triebwagen",
    }


class Personenwaggon(Waggon, db.Model):
    __tablename__ = 'personenwaggons'
    sitzanzahl = db.Column(db.Integer)
    gewicht = db.Column(db.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "personenwaggon",
    }

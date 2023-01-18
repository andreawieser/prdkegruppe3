from flask import Blueprint, render_template, flash, redirect, url_for
from website.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from website import db
from flask_wtf import FlaskForm
# The biggest advantage of WTForms is that it contains rules for email and password validations
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email
from flask_login import login_user, login_required, logout_user, current_user
from functools import wraps

auth = Blueprint("auth", __name__)


# define a decorator whereupon a function only gets triggered if the user is an admin
# and returns the user to the login page if he is not
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_admin:
            return f(*args, **kwargs)
        else:
            flash("You need to be an admin to view this page.", category="danger")
            return redirect(url_for('auth.login'))
    return wrap


# defines the login form
class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    # remember field allows users to stay logged in after closing the browsers using a secure cookie
    remember = BooleanField(label="Remember Me")
    submit = SubmitField(label="Login")


# parameter methods shows which methods get accepted by the route
# handles the login-procedure
@auth.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        # create first admin if not yet created
        if not User.query.filter(User.email == 'admin@zug.at').first():
            db.session.commit()
            user = User(
                email='admin@zug.at',
                password=generate_password_hash("admin", method="sha256"),
                is_admin=True
            )
            db.session.add(user)
            db.session.commit()
            print("admin created!")

        # create first employee if not yet created
        if not User.query.filter(User.email == 'emp@zug.at').first():
            user = User(
                email='emp@zug.at',
                password=generate_password_hash("emp", method="sha256")
            )
            db.session.add(user)
            db.session.commit()
            print("employee created!")

        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                # the categories success and danger are categories of bootstrap
                flash(f"Willkommen zurück {user.email}!", category="success")
                login_user(user, remember=form.remember.data)
                return redirect(url_for("views.home"))
            else:
                flash("Passwort ist falsch, versuche es nochmal.", category="danger")
        else:
            flash("E-Mail existiert nicht.", category="danger")

    return render_template("login.html", form=form, user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

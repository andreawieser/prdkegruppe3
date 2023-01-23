from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy import MetaData

# metadata is a fix to Flask Migrate "ValueError: Constraint must have a name"
metadata = MetaData(
    naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }
)

# creating a SQLAlchemy database instance -> with that we can represent the database as classes (= models)
db = SQLAlchemy(metadata=metadata)
DB_NAME = "site.db"
#DB_NAME = "test.db"


def create_app():
    app = Flask(__name__)
    # the secret key is mandatory e.g. for csrf protection, that means it will protect against modifying cookies,
    # cross site request, forgery attacks etc.
    app.config["SECRET_KEY"] = "bdd96e66c3fbb1a20a12a36144769328"
    app.config['JSON_SORT_KEYS'] = False
    # export FLASK_APP = main.py

    # SQLAlchemy allows to represent the database structure as classes (called models)
    # with the three /// ist is possible to represent a relative path
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    # telling the database which app to use
    db.init_app(app)
    migrate = Migrate(app, db, render_as_batch=True)

    from .views import views
    from .auth import auth
    from .api import api

    # register the blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api')

    # the following import is to make sure models.py runs and defines the classes before creating the database
    # it is important to import all models individually
    # it's location is deliberate, otherwise it would run an error
    from .models import User, Triebwagen, Personenwaggon, Waggon, Zug

    create_database(app)

    # allows users to login and logout and access sites which are not accessible when not logged in
    # works with sessions (temporary storages your computer has with websites, e.g. for not having to log in every time
    # but being logged in automatically
    login_manager = LoginManager()
    # where to redirect the user if he is not logged in and there is a login required
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # telling flask how to load a user
    @login_manager.user_loader
    def load_user(id):
        # query.get by default searches for the primary key
        return User.query.get(int(id))

    return app


# check if the database already exists and if it doesn't, create it
def create_database(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Created database!")

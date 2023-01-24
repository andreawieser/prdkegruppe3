from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TimeField, IntegerField, RadioField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import NumberRange
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

import api
from app.models import User


# Submit-Felder zur mehrfachen Verwendung

class EmptyForm(FlaskForm):
    cancel = SubmitField('Abbrechen')
    submit = SubmitField('Submit')


# Eingabefelder für "Login"

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Eingeloggt bleiben')
    submit = SubmitField('Login')


# Eingabefelder für "Neue Aktion festlegen"

class PromotionForm(FlaskForm):
    start_date = DateField('Von', format='%Y-%m-%d', default=datetime.today,
                           validators=[DataRequired('Startdatum auswählen: ')])
    end_date = DateField('Bis', format='%Y-%m-%d', default=datetime.today,
                         validators=[DataRequired('Enddatum auswählen: ')])
    sale = IntegerField('Rabatt in Prozent: ',
                        validators=[DataRequired('Prozentsatz zwischen 1 und 100'), NumberRange(min=1, max=100)])
    route = SelectField('Strecke auswählen:', choices=api.get_route_name(), validators=[DataRequired()])
    validity = RadioField('Label', choices=['Preisnachlass für alle Fahrtstrecken',
                                            'Preisnachlass für ausgewählte Fahrtstrecke'],
                          default='Preisnachlass für alle Fahrtstrecken', validators=[DataRequired()])
    submit = SubmitField('Aktion festlegen')

    # Das gewählte Datum wird überprüft und falls es in der Vergangenheit liegt ein Fehler ausgegeben

    def validate_start_date(self, start_date):
        today = datetime.now()
        if start_date.data < today.date():
            raise ValidationError('Der gewählte Tag liegt in der Vergangenheit.')

    # Das gewählte Datum wird überprüft und falls es in der Vergangenheit liegt ein Fehler ausgegeben
    # das Enddatum wird mit dem Startdatum verglichen und falls es kleiner ist, wird ein Fehler ausgegeben

    def validate_end_date(self, end_date):
        today = datetime.now()
        if end_date.data < today.date():
            raise ValidationError('Der gewählte Tag liegt in der Vergangenheit.')
        elif self.start_date.data > end_date.data:
            raise ValidationError('Das Enddatum ist vor dem Startdatum.')


# Eingabefelder für "Registrierung"

class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

    # Benutzername und E-Mail werden eingelesen und geprüft, ob diese schon in Gebrauch sind
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Dieser Benutzername ist schon vergeben.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Zu dieser Email-Adresse existiert bereits ein Nutzer.')


# Eingabefelder für "Meine Daten"

class EditProfileForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    oldPassword = PasswordField('Altes Passwort')
    newPassword = PasswordField('Neues Passwort')
    newPassword2 = PasswordField('Neues Passwort wiederholen', validators=[EqualTo('newPassword')])
    submit = SubmitField('Daten ändern')
    delete = SubmitField('Profil löschen')

    # Benutzername und E-Mail sind bereits mit den vorhandenen Daten vorausgefüllt
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    # Benutzername und E-Mail werden eingelesen und geprüft, ob diese schon in Gebrauch sind
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Dieser Benutzername ist schon vergeben.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Zu dieser Email-Adresse existiert bereits ein Nutzer.')


# Eingabefelder für "Ticket suchen"

class TicketForm(FlaskForm):
    departure = SelectField('Von', choices=api.get_station(), validators=[DataRequired()])
    destination = SelectField('Nach', choices=api.get_station(), validators=[DataRequired()])
    date = DateField('Wann', format='%Y-%m-%d', default=datetime.today,
                     validators=[DataRequired('Startdatum auswählen: ')])
    time = TimeField('Wann', format='%H:%M', default=datetime.today, validators=[DataRequired()])
    submit = SubmitField('Suchen')

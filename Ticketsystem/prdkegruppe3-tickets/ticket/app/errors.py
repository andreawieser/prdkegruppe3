from flask import render_template
from app import app, db


# Fehlerbehandlung - bei Error wird das entsprechende Template geladen

@app.errorhandler(404)
def not_found_error():
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error():
    db.session.rollback()
    return render_template('500.html'), 500

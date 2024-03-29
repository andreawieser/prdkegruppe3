from app import app, db
from app.models import User

# Gibt den Shell-Kontext für eine interaktive Shell zurück

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

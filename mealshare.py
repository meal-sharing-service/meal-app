from app import app, db
from app.models import User, Offer

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Offer': Offer}
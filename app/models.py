from datetime import datetime
from app import db, login, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from time import time
import jwt
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    address = db.Column(db.String(128))
    postal_code = db.Column(db.String(64))
    state_province = db.Column(db.String(64))
    country = db.Column(db.String(64))
    interest = db.Column(db.String(128))
    lat = db.Column(db.Float())
    lng = db.Column(db.Float())
    offers = db.relationship('Offer', backref='author', lazy='dynamic')
    orders = db.relationship('Order', backref='recipient', lazy='dynamic')
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def __repr__(self):
        return '<User {}>'.format(self.username)    
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.String(140))
    pickup = db.Column(db.String(140))
    servings = db.Column(db.Integer)
    claims = db.Column(db.Integer,default=0)
    expiration = db.Column(db.String(64))
    category_id = db.Column(db.Integer)
    request = db.Column(db.Boolean)
    condition = db.Column(db.String(64))
    image_public_id = db.Column(db.String(128))
    image_thumbnail = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Offer {}>'.format(self.title)

"""
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    ingredients = db.relationship("Ingredient", secondary="IngredientList")

    def __repr__(self):
        return '<Recipe {}>'.format(self.name)


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    ingredients = db.relationship("Recipe", secondary="ingredientList")

    def __repr__(self):
        return '<Offer {}>'.format(self.title)


class IngredientList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))

    recipe = db.relationship(Recipe, backref=db.backref("ingredientList", cascade="all, delete-orphan"))
    recipe = db.relationship(Ingredient, backref=db.backref("ingredientList", cascade="all, delete-orphan"))

    def __repr__(self):
        return '<Offer {}>'.format(self.title)
"""

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    offer_id = db.Column(db.Integer, db.ForeignKey('offer.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    users = db.relationship('User', backref="order")
    offer = db.relationship('Offer', backref="orders")
    
    def __repr__(self):
        return '<Order {}>'.format(self.id)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://postgres:ItemStore@localhost/storecatalog')
db = SQLAlchemy(app)


class User(db.Model):
    # Stores different users info
    __tablename__ = 'user'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(250), nullable=False)
    email = db.Column(String(250), nullable=False)
    picture = db.Column(String(250))


class Accessory(db.Model):
    # Store contains accessory items for varies products
    __tablename__ = 'Accessory'

    name = db.Column(String(50), nullable=False)
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('user.id'))
    user = db.relationship(User)


class AccessorySection(db.Model):
    # Driven from the Accessory class making branches from it
    __tablename__ = 'Accessory-Section'

    name = db.Column(String(50), nullable=False)
    id = db.Column(Integer, primary_key=True)
    store_id = db.Column(Integer, ForeignKey('Accessory.id'))
    accessory = db.relationship(Accessory)
    user_id = db.Column(Integer, ForeignKey('user.id'))
    user = db.relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'store_id': self.store_id
        }


class SectionItem(db.Model):
    # Driven from Acessory section making branch from it
    __tablename__ = 'cables'

    name = db.Column(String(50), nullable=False)
    id = db.Column(Integer, primary_key=True)
    price = db.Column(String(8))
    description = db.Column(String(250))
    image_url = db.Column(String(250))
    store_id = db.Column(Integer, ForeignKey('Accessory-Section.id'))
    category = db.relationship(AccessorySection)
    user_id = db.Column(Integer, ForeignKey('user.id'))
    user = db.relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'price': self.price,
            'description': self.description,
            'image_url': self.image_url,
            'store_id': self.store_id
        }

db.create_all()

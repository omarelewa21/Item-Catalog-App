import sys
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Accessory(Base):
    # Store contains accessory items for varies products
    __tablename__ = 'Accessory'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)


class AccessorySection(Base):
    # Driven from the Accessory class making branches from it
    __tablename__ = 'Accessory-Section'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('Accessory.id'))
    accessory = relationship(Accessory)


class SectionItem(Base):
    # Driven from Acessory section making branch from it
    __tablename__ = 'cables'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    price = Column(String(8))
    description = Column(String(250))
    image_url = Column(String(250))
    store_id = Column(Integer, ForeignKey('Accessory-Section.id'))
    category = relationship(AccessorySection)


engine = create_engine('sqlite:///mobilystore.db')
Base.metadata.create_all(engine)

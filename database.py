import sys
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# Head of the tree


class Accessory(Base):
    # Store contains accessory items for varies products
    __tablename__ = 'Accessory'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)


# Children of the Accessory tree


class MobileAccessory(Base):
    # Contains all accessory items for Mobiles
    __tablename__ = 'Mobile_Acc'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('Accessory.id'))
    accessory = relationship(Accessory)


class ComputerAccessory(Base):
    # Contains all accessory items for PCs
    __tablename__ = 'PC_Acc'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('Accessory.id'))
    accessory = relationship(Accessory)


# Children of Mobile Accessory branch


class Cables(Base):
    # A category of mobile accessories
    __tablename__ = 'cables'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    price = Column(String(8))
    description = Column(String(250))
    image_url = Column(String(250))
    store_id = Column(Integer, ForeignKey('MobileAccessory.id'))
    accessory = relationship(MobileAccessory)


class Chargers(Base):
    # A category of mobile accessories
    __tablename__ = 'chargers'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    price = Column(String(8))
    description = Column(String(250))
    image_url = Column(String(250))
    store_id = Column(Integer, ForeignKey('MobileAccessory.id'))
    accessory = relationship(MobileAccessory)


class Headsets(Base):
    # A category of mobile accessories
    __tablename__ = 'Headsets'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    price = Column(String(8))
    description = Column(String(250))
    image_url = Column(String(250))
    store_id = Column(Integer, ForeignKey('MobileAccessory.id'))
    accessory = relationship(MobileAccessory)


# Children of Computer Accessory branch 


class Mouses(Base):
    # A category of computer accessories
    __tablename__ = 'Mouses'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    price = Column(String(8))
    description = Column(String(250))
    image_url = Column(String(250))
    store_id = Column(Integer, ForeignKey('ComputerAccessory.id'))
    accessory = relationship(ComputerAccessory)


class KeyBoards(Base):
    # A category of computer accessories
    __tablename__ = 'keyboards'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    price = Column(String(8))
    description = Column(String(250))
    image_url = Column(String(250))
    store_id = Column(Integer, ForeignKey('ComputerAccessory.id'))
    accessory = relationship(ComputerAccessory)


class FlashDrives(Base):
    # A category of computer accessories
    __tablename__ = 'flash_drives'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    price = Column(String(8))
    description = Column(String(250))
    image_url = Column(String(250))
    store_id = Column(Integer, ForeignKey('ComputerAccessory.id'))
    accessory = relationship(ComputerAccessory)


engine = create_engine('sqlite:///mobilystore.db')
Base.metadata.create_all(engine)

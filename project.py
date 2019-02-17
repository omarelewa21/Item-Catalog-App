from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from database import Accessory, AccessorySection, SectionItem

app = Flask(__name__)

engine = create_engine('sqlite:///mobilystore.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/mobily')
def mobilystore():
    all_cables = session.query(SectionItem).filter(
        SectionItem.store_id == 1).all()
    return render_template(
        'mainpage.html', all_cables=all_cables)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from database import Accessory, AccessorySection, SectionItem

app = Flask(__name__)

engine = create_engine('sqlite:///mobilystore.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/mobily/categories/json')
def categoriesJson():
    category = session.query(AccessorySection).all()
    return jsonify(categories=[i.serialize for i in category])


@app.route('/mobily/<int:category_id>/items/json')
def itemJson(category_id):
    item = session.query(SectionItem).filter_by(store_id=category_id).all()
    return jsonify(items=[i.serialize for i in item])


@app.route('/')
@app.route('/mobily')
def mobilystore():
    mobile_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 1).all()
    PC_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 2).all()

    all_cables = session.query(SectionItem).filter(
        SectionItem.store_id == 1).all()
    all_chargers = session.query(SectionItem).filter(
        SectionItem.store_id == 2).all()
    all_headsets = session.query(SectionItem).filter(
        SectionItem.store_id == 3).all()
    all_mouses = session.query(SectionItem).filter(
        SectionItem.store_id == 4). all()
    all_keyboards = session.query(SectionItem).filter(
        SectionItem.store_id == 5).all()
    all_drivers = session.query(SectionItem).filter(
        SectionItem.store_id == 6).all()

    return render_template(
        'mainpage.html', mobile_items=mobile_items,
        PC_items=PC_items, all_cables=all_cables,
        all_chargers=all_chargers, all_headsets=all_headsets,
        all_mouses=all_mouses, all_keyboards=all_keyboards,
        all_drivers=all_drivers)


@app.route('/mobily/<int:item_id>')
def itemdetail(item_id):
    item = session.query(SectionItem).filter_by(id=item_id).one()
    return render_template('itemdetail.html', item=item)


@app.route('/mobily/new/<int:store__id>', methods=['GET', 'POST'])
def newItem(store__id):
    if request.method == 'POST':
        newItem = SectionItem(
            name=request.form['name'],
            store_id=store__id,
            price=request.form['price'],
            description=request.form['description'],
            image_url=request.form['image_url']
        )
        session.add(newItem)
        session.commit()
        # Flash message
        flash("New Item Created")
        # return to previous page
        if store__id == 1:
            return redirect(url_for('cables_store'))
        elif store__id == 2:
            return redirect(url_for('chargers_store'))
        elif store__id == 3:
            return redirect(url_for('headsets_store'))
        elif store__id == 4:
            return redirect(url_for('mouses_store'))
        elif store__id == 5:
            return redirect(url_for('keyboards_store'))
        elif store__id == 6:
            return redirect(url_for('drives_store'))

    else:
        return render_template('newitem.html', store__id=store__id)


@app.route('/mobily/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    item = session.query(SectionItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']
        item.description = request.form['description']
        item.image_url = request.form['image_url']
        session.add(item)
        session.commit()
        return redirect(url_for('itemdetail', item_id=item.id))
    else:
        return render_template('edititem.html', item=item)


@app.route('/mobily/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(item_id):
    item = session.query(SectionItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('mobilystore'))
    else:
        return render_template('deleteitem.html', item=item)


@app.route('/mobily/cables')
def cables_store():
    mobile_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 1).all()
    PC_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 2).all()
    all_cables = session.query(SectionItem).filter(
        SectionItem.store_id == 1).all()
    return render_template(
        'cables.html', all_cables=all_cables,
        mobile_items=mobile_items, PC_items=PC_items)


@app.route('/mobily/chargers')
def chargers_store():
    mobile_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 1).all()
    PC_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 2).all()
    all_chargers = session.query(SectionItem).filter(
        SectionItem.store_id == 2).all()
    return render_template(
        'chargers.html', all_chargers=all_chargers,
        mobile_items=mobile_items, PC_items=PC_items)


@app.route('/mobily/headsets')
def headsets_store():
    mobile_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 1).all()
    PC_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 2).all()
    all_headsets = session.query(SectionItem).filter(
        SectionItem.store_id == 3).all()
    return render_template(
        'headsets.html', all_headsets=all_headsets,
        mobile_items=mobile_items, PC_items=PC_items)


@app.route('/mobily/mouses')
def mouses_store():
    mobile_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 1).all()
    PC_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 2).all()
    all_mouses = session.query(SectionItem).filter(
        SectionItem.store_id == 4).all()
    return render_template(
        'mouses.html', all_mouses=all_mouses,
        mobile_items=mobile_items, PC_items=PC_items)


@app.route('/mobily/keyboards')
def keyboards_store():
    mobile_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 1).all()
    PC_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 2).all()
    all_keyboards = session.query(SectionItem).filter(
        SectionItem.store_id == 5).all()
    return render_template(
        'keyboards.html', all_keyboards=all_keyboards,
        mobile_items=mobile_items, PC_items=PC_items)


@app.route('/mobily/drives')
def drives_store():
    mobile_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 1).all()
    PC_items = session.query(AccessorySection).filter(
        AccessorySection.store_id == 2).all()
    all_drivers = session.query(SectionItem).filter(
        SectionItem.store_id == 6).all()
    return render_template(
        'drives.html', all_drivers=all_drivers,
        mobile_items=mobile_items, PC_items=PC_items)

if __name__ == '__main__':
    app.secret_key = 'suoer_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

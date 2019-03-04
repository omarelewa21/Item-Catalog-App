from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from database import Accessory, AccessorySection, SectionItem, User
# Imports for security features
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

engine = create_engine('sqlite:///mobilystore.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Login page
@app.route('/login')
def showlogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32)
        )
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps(
                'Current user is already connected.'), 200
                )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if the user exists, if not, make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style =
                        "width: 300px; height: 300px;border-radius:
                            150px;-webkit-border-radius:
                            150px;-moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'),
            401
            )
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = (
        'https://accounts.google.com/o/oauth2/revoke?token=%s' %
        login_session['access_token']
        )
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400)
            )
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    # Store user in the database
    newUser = User(name=login_session['username'], email=login_session[
                'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    # return user info
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    # return user ID
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


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

    if 'username' not in login_session:
        return render_template(
            'mainpage_notLoggedin.html', mobile_items=mobile_items,
            PC_items=PC_items, all_cables=all_cables,
            all_chargers=all_chargers, all_headsets=all_headsets,
            all_mouses=all_mouses, all_keyboards=all_keyboards,
            all_drivers=all_drivers)
    else:
        return render_template(
            'mainpage_Loggedin.html', mobile_items=mobile_items,
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
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = SectionItem(
            name=request.form['name'],
            store_id=store__id,
            price=request.form['price'],
            description=request.form['description'],
            image_url=request.form['image_url'],
            user_id=login_session['user_id']
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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

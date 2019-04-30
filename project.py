#!/bin/sh
import os
import sys
from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from database import Accessory, AccessorySection, SectionItem, User
from database import db, app
import psycopg2
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

app = app
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog App"


@app.route('/login')
def showlogin():
    # Login page
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
    db.session.add(newUser)
    db.session.commit()
    user = User.query.filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    # return user info
    user = User.query.filter_by(id=user_id).one()
    return user


def getUserID(email):
    # return user ID
    try:
        user = User.query.filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/mobily/categories/json')
def categoriesJson():
    # Jsonify all the category sections in database
    category = AccessorySection.query.all()
    return jsonify(categories=[i.serialize for i in category])


@app.route('/mobily/<int:category_id>/items/json')
def itemJson(category_id):
    # Jsonify all the items in a category sections
    item = SectionItem.query.filter_by(store_id=category_id).all()
    return jsonify(items=[i.serialize for i in item])


@app.route('/mobily/<int:item_id>/itemdetail/json')
def itemdetailjson(item_id):
    # Jsonify the details specfic for one item
    item = SectionItem.query.filter_by(id=item_id).one()
    return jsonify(item_details=item.serialize)


@app.route('/')
@app.route('/mobily')
def mobilystore():
    # Main page for the Mobily Store
    mobile_items = AccessorySection.query.filter(
        AccessorySection.store_id == 1).all()
    PC_items = AccessorySection.query.filter(
        AccessorySection.store_id == 2).all()
    # Storing each cateogry items in a variable
    # In order to render an item from each category on the page
    all_cables = SectionItem.query.filter(
        SectionItem.store_id == 1).all()
    all_chargers = SectionItem.query.filter(
        SectionItem.store_id == 2).all()
    all_headsets = SectionItem.query.filter(
        SectionItem.store_id == 3).all()
    all_mouses = SectionItem.query.filter(
        SectionItem.store_id == 4). all()
    all_keyboards = SectionItem.query.filter(
        SectionItem.store_id == 5).all()
    all_drivers = SectionItem.query.filter(
        SectionItem.store_id == 6).all()
    # Checking if the user is logged in or not
    if 'username' not in login_session:
        # rendering page contains a login button
        return render_template(
            'mainpage_notLoggedin.html', mobile_items=mobile_items,
            PC_items=PC_items, all_cables=all_cables,
            all_chargers=all_chargers, all_headsets=all_headsets,
            all_mouses=all_mouses, all_keyboards=all_keyboards,
            all_drivers=all_drivers)
    else:
        # rendering page contains a logout button
        return render_template(
            'mainpage_Loggedin.html', mobile_items=mobile_items,
            PC_items=PC_items, all_cables=all_cables,
            all_chargers=all_chargers, all_headsets=all_headsets,
            all_mouses=all_mouses, all_keyboards=all_keyboards,
            all_drivers=all_drivers)


@app.route('/mobily/category/<int:category_id>')
def category_store(category_id):
    # Display a navigation bar as the same of the main page
    # Dispaly all items specific to one category
    mobile_items = AccessorySection.query.filter(
        AccessorySection.store_id == 1).all()
    PC_items = AccessorySection.query.filter(
        AccessorySection.store_id == 2).all()
    # Refer to Cateogry ID by store_id to obtain all items for that category
    category_items = SectionItem.query.filter_by(
        store_id=category_id)

    return render_template(
        'category.html', category_items=category_items,
        mobile_items=mobile_items, PC_items=PC_items,
        store__id=category_id)


@app.route('/mobily/item/<int:item_id>')
def itemdetail(item_id):
    # Display item information
    item = SectionItem.query.filter_by(id=item_id).one()
    return render_template('itemdetail.html', item=item)


@app.route('/mobily/<int:store__id>/newitem', methods=['GET', 'POST'])
def newItem(store__id):
    # Renders a form to insert a new item
    if 'username' not in login_session:
        # Checks if the user is logged in to enable the feature
        return redirect('/login')

    if request.method == 'POST':
        newItem = SectionItem(
            name=request.form['name'],
            store_id=store__id,
            price=request.form['price'],
            description=request.form['description'],
            image_url=request.form['image_url'],
            user_id=getUserID(login_session['email'])
        )
        db.session.add(newItem)
        db.session.commit()
        # Flash message
        flash("New Item Created")
        # redirect to the previous category page
        return redirect(url_for('category_store', category_id=store__id))
    else:
        return render_template('newitem.html', store__id=store__id)


@app.route('/mobily/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    # Renders a a form to edit an item
    if 'username' not in login_session:
        # Checks if the user is logged in to enable the feature
        return redirect('/login')
    item = SectionItem.query.filter_by(id=item_id).one()
    user = SectionItem.query.filter_by(id=item.user_id).one()
    # Checks if the user is created the item to delete it
    # if not returns not authoraized
    if user.email != login_session['email']:
        return "Not authorized to edit this item"
    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']
        item.description = request.form['description']
        item.image_url = request.form['image_url']
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('itemdetail', item_id=item.id))
    else:
        return render_template('edititem.html', item=item)


@app.route('/mobily/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(item_id):
    # Renders two buttons, one for deleting an item and another for cancelling
    if 'username' not in login_session:
        # Checks if the user is logged in to enable the feature
        return redirect('/login')
    item = SectionItem.query.filter_by(id=item_id).one()
    user = User.query.filter_by(id=item.user_id).one()
    # Checks if the user is created the item to delete it
    # if not returns not authoraized
    if user.email != login_session['email']:
        return "Not authorized to edit this item"
    if request.method == 'POST':
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for('mobilystore'))
    else:
        return render_template('deleteitem.html', item=item)

app.debug = True
app.secret_key = 'super_secret_key'

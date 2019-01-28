from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User

#new imports for creating unique session token
from flask import session as login_session
import random, string

#imports for google login
from oauth2client.client import flow_from_clientsecrets #creats a flow from our client secret, a json formated style that stores  client id, client secret and other oauth2.0 parameters
from oauth2client.client import FlowExchangeError #if running into error while exchanging authorization token for access token
import httplib2 #HTTP client library in python
import json
from flask import make_response #converts return value from function into a real response obj we can send to client
import requests #Apache 2.0 licensed HTTP library written in python

CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

#Connect to Database and create database session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#create a state token to prevent requests forgery
#store it in the session for later validation
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    #render the login template
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=["POST"])
def gconnect():
    # get the parameters from the post request and check to see the token that our server sent to client matches the one they are giving us
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'),401)
        response.headers['Content-type'] = 'application/json'
        return response
    #if the state tokens match, then get the google one time use code
    code = request.data
    try:
        #upgrade the authorization code into a credentials object
        #create oauth flow, add client secret key information to it
        oauth_flow = flow_from_clientsecrets('client_secrets.json',scope='')
        oauth_flow.redirect_uri = 'postmessage' #specify with postmessage this is the one time code
        credentials = oauth_flow.step2_exchange(code) #trade auth code for cred code
    #if there are any errors in exchanging codes
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response

    #if it worked, check to see if access token is valid by doing an HTTP request to the google api
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
    h=httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    #if there is an error in the access token, abort mission
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),500)
        response.headers['Content-type'] = 'application/json'
        return response
    #if there are no errors, now lets make sure the access code's id matches the id of the user login into our server
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID"),401)
        response.headers['Content-type'] = 'application/json'
        return response

    #verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's user ID doesn't match app's ID"),401)
        response.headers['Content-type'] = 'application/json'
        return response     

    #check to see if user is already logged in
    # stored_credentials = login_session.get('credentials')
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # if stored_credentials is not None and gplus_id == stored_gplus_id:
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("Current user is already connected"),200)
        response.headers['Content-type'] = 'application/json'
        return response
    #store the access token in the sessions for later use
    # login_session['credentials'] = credentials
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    #get user info from gplus
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params= params)

    # data = json.load(answer.text)
    data = answer.json()

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    output = ''
    output += '<h1>Welcome,'
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect/')
def gdisconnect():
    #only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        print "Access Token is none"
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    #Execute HTTP GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    #if revoking was successful, reset the user's sessions and send user a 200 response
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected'),200)
        response.headers['Content-type'] = 'application/json'
        return response
    else:
        #for whatever reason, the given token was invalid
        response = make_response(json.dumps('Failed to revoke token for given user'),400)
        response.headers['Content-type'] = 'application/json'
        return response


#JSON APIs to view Restaurant Information
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(Menu_Item = Menu_Item.serialize)

@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants= [r.serialize for r in restaurants])


#Show all restaurants
@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
    restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
    return render_template('restaurants.html', restaurants = restaurants)

#Create a new restaurant
@app.route('/restaurant/new/', methods=['GET','POST'])
def newRestaurant():
    #if there is no one logged in, then redirect them to login page
    if 'username' not in login_session:
        flash('You must login first')
        return redirect('/login')
    if request.method == 'POST':
        newRestaurant = Restaurant(name = request.form['name'])
        session.add(newRestaurant)
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

#Edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    #if there is no one logged in, then redirect them to login page
    if 'username' not in login_session:
        flash('You must login first')
        return redirect('/login')
    editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant = editedRestaurant)


#Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
    #if there is no one logged in, then redirect them to login page
    if 'username' not in login_session:
        flash('You must login first')
        return redirect('/login')
    restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        session.commit()
        return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))
    else:
        return render_template('deleteRestaurant.html',restaurant = restaurantToDelete)

#Show a restaurant menu
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return render_template('menu.html', items = items, restaurant = restaurant)
     


#Create a new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
def newMenuItem(restaurant_id):
    #if there is no one logged in, then redirect them to login page
    if 'username' not in login_session:
        flash('You must login first')
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id = restaurant_id)

#Edit a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    #if there is no one logged in, then redirect them to login page
    if 'username' not in login_session:
        flash('You must login first')
        return redirect('/login')
    editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit() 
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = editedItem)


#Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    #if there is no one logged in, then redirect them to login page
    if 'username' not in login_session:
        flash('You must login first')
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id = menu_id).one() 
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item = itemToDelete)




if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)

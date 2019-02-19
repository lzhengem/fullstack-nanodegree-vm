from models import Base, User, Product
from flask import Flask, jsonify, request, url_for, abort, g
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from flask_httpauth import HTTPBasicAuth

#imports for google login
from oauth2client.client import flow_from_clientsecrets #creats a flow from our client secret, a json formated style that stores  client id, client secret and other oauth2.0 parameters
from oauth2client.client import FlowExchangeError #if running into error while exchanging authorization token for access token
from flask import make_response
import httplib2 #HTTP client library in python
auth = HTTPBasicAuth()


engine = create_engine('sqlite:///regalTree.db',connect_args = {'check_same_thread': False})

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)




#ADD @auth.verify_password decorator here. should return true or false
@auth.verify_password
def verify_password(username_or_token, password):
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True



#add /token route here to get a token for a user with login credentials
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()    
    return jsonify({'token' : token.decode('ascii')})




@app.route('/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print "missing arguments"
        abort(400) 
        
    if session.query(User).filter_by(username = username).first() is not None:
        print "existing user"
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message':'user already exists'}), 200#, {'Location': url_for('get_user', id = user.id, _external = True)}
        
    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ 'username': user.username }), 201#, {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

@app.route('/products', methods = ['GET', 'POST'])
@auth.login_required
def showAllProducts():
    if request.method == 'GET':
        products = session.query(Product).all()
        return jsonify(products = [p.serialize for p in products])
    if request.method == 'POST':
        name = request.json.get('name')
        category = request.json.get('category')
        price = request.json.get('price')
        newItem = Product(name = name, category = category, price = price)
        session.add(newItem)
        session.commit()
        return jsonify(newItem.serialize)



@app.route('/products/<category>')
@auth.login_required
def showCategoriedProducts(category):
    if category == 'fruit':
        fruit_items = session.query(Product).filter_by(category = 'fruit').all()
        return jsonify(fruit_products = [f.serialize for f in fruit_items])
    if category == 'legume':
        legume_items = session.query(Product).filter_by(category = 'legume').all()
        return jsonify(legume_products = [l.serialize for l in legume_items])
    if category == 'vegetable':
        vegetable_items = session.query(Product).filter_by(category = 'vegetable').all()
        return jsonify(produce_products = [p.serialize for p in produce_items])


@app.route('/oauth/<provider>',methods = ['POST'])
def login(provider):
    if provider == 'google':
        #STEP 1 - Parse the auth code
        auth_code = request.json.get('auth_code')
        #STEP 2 - Exchange for token
        try:
            oauth_flow = flow_from_clientsecrets('client_secrets.json',scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.jumps('Failed to upgrade the authorizaton code.'), 401)
            response.headers['Content-type'] = 'application/json'
            return response
        #STEP 3 - FInd user or make a new one

        #get user info
        h = httplib2.Http()
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()
        name = data['name']
        picture = data['picture']
        email = data['email']

        #see if user exists, if it doesn't, make a new one
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username = name, picture = picture, email=email)
            session.add(user)
            session.commit()

        #step 4 - Make token
        token = user.generate_auth_token(600)

        #STEP 5 - send back token to the client
        return jsonify({'token' : token.decode('ascii')})

        # return jsonify({'token' : token.decode('ascii'),'duration':600})
    else:
        return 'Unrecoginized Provider'
    


if __name__ == '__main__':
    app.debug = True
    #app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(host='0.0.0.0', port=5000)
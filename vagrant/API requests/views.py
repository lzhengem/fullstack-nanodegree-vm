from findARestaurant import findARestaurant
from models import Base, Restaurant
from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)




#foursquare_client_id = ''

#foursquare_client_secret = ''

#google_api_key = ''

engine = create_engine('sqlite:///restaurants.db',connect_args={'check_same_thread':False})

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

@app.route('/restaurants', methods = ['GET', 'POST'])
def all_restaurants_handler():
  #YOUR CODE HERE
    if request.method == 'GET':
        restaurant = session.query(Restaurant).all()
        return jsonify(restaurants = [i.serialize for i in restaurant])

    elif request.method == 'POST':
        location = request.args.get('location','')
        mealtype = request.args.get('mealtype','')
        restaurant_info = findARestaurant(request.args.get('mealtype'), request.args.get('location'))
        if restaurant_info != "No Restaurants Found":
            # return jsonify(restaurant_info)
            restaurant = Restaurant(restaurant_name= restaurant_info["restaurant_name"], restaurant_address= restaurant_info["restaurant_address"], restaurant_image = restaurant_info["restaurant_image"] )
            session.add(restaurant)
            session.commit()
            return jsonify(restaurant.serialize)
            # all_restaurant = session.query(Restaurant).all()
            # print 'all:' 
            # print all_restaurant
        else:
            return jsonify({"error":"No Restaurants Found for %s in %s" % (mealType, location)})

    
    
@app.route('/restaurants/<int:id>', methods = ['GET','PUT', 'DELETE'])
def restaurant_handler(id):
  #YOUR CODE HERE
  if request.method == 'GET':
    return 'hi'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
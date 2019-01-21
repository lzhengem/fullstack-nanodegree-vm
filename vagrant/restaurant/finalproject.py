from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__)

# engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread':False})
# Base.metadata.bind = engine
# DBSession = sessionmaker(bind = engine)
# session = DBSession()


#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

@app.route("/")
@app.route("/restaurants/")
def showRestaurants():
    return render_template('restaurants.html', restaurants=restaurants)

@app.route("/restaurant/new/")
def newRestaurant():
    return render_template('newRestaurant.html')

@app.route("/restaurant/<int:restaurant_id>/edit/")
def editRestaurant(restaurant_id):
    return render_template('editRestaurant.html',restaurant=restaurant)

@app.route("/restaurant/<int:restaurant_id>/")
@app.route("/restaurant/<int:restaurant_id>/menu/")
def showMenu(restaurant_id):
    return render_template('menu.html', restaurant=restaurant, items = items)

@app.route("/restaurant/<int:restaurant_id>/new/")
def newMenuItem(restaurant_id):
    return render_template('newMenuItem.html')

@app.route("/restaurant/<int:restaurant_id>/<int:menu_id>/edit/")
def editMenuItem(restaurant_id,menu_id):
    return render_template('editMenuItem.html',restaurant=restaurant, item=item)

@app.route("/restaurant/<int:restaurant_id>/<int:menu_id>/delete/")
def deleteMenuItem(restaurant_id,menu_id):
    return "This page is for deleting menu item %s" % menu_id



if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
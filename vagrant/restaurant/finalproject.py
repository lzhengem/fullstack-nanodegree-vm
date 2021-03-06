from flask import Flask, render_template, url_for, redirect, request, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread':False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


@app.route("/")
@app.route("/restaurants/")
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)

@app.route("/restaurant/new/", methods=["GET","POST"])
def newRestaurant():
    if request.method == "POST":
        if request.form["name"]:
            name = request.form["name"]
            restaurant = Restaurant(name = name)
            session.add(restaurant)
            session.commit()
            flash("New restaurant %s created!" % name)
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

@app.route("/restaurant/<int:restaurant_id>/edit/",methods=["GET","POST"])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST': #if it was a post request
        if request.form['name']: #and if they entered a name, update it in the database
            name = request.form['name']
            restaurant.name = name
            session.add(restaurant)
            session.commit()
            flash("%s has been edited " % name)
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html',restaurant=restaurant)

@app.route("/restaurant/<int:restaurant_id>/delete/", methods=["GET","POST"])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == "POST":
        name = restaurant.name
        session.delete(restaurant)
        session.commit()
        flash("%s has been deleted " % name)
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html',restaurant=restaurant)

@app.route("/restaurant/<int:restaurant_id>/")
@app.route("/restaurant/<int:restaurant_id>/menu/")
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('menu.html', restaurant=restaurant, items = items)

@app.route("/restaurant/<int:restaurant_id>/new/",methods=["GET","POST"])
def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == "POST":
        if request.form["name"]:
            name = request.form["name"]
            item = MenuItem(name = name, restaurant_id=restaurant.id,
                            description=request.form["description"],price=request.form["price"],
                            course=request.form["course"])
            session.add(item)
            session.commit()
            flash(" %s has been created" % name)
        return redirect(url_for('showMenu', restaurant_id =restaurant.id))
    else:
        return render_template('newMenuItem.html',restaurant=restaurant)

@app.route("/restaurant/<int:restaurant_id>/<int:menu_id>/edit/", methods=["GET","POST"])
def editMenuItem(restaurant_id,menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == "POST":
        if request.form["name"]:
            item.name = request.form["name"]
        item.description=request.form["description"]
        item.price=request.form["price"]
        item.course=request.form["course"]
        session.add(item)
        session.commit()
        flash(" %s has been edited" % item.name)
        return redirect(url_for('showMenu', restaurant_id =restaurant.id))

    return render_template('editMenuItem.html',restaurant=restaurant, item=item)

@app.route("/restaurant/<int:restaurant_id>/<int:menu_id>/delete/", methods=["GET","POST"])
def deleteMenuItem(restaurant_id,menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == "POST":
        name = item.name
        session.delete(item)
        session.commit()
        flash(" %s has been deleted" % name)
        return redirect(url_for('showMenu', restaurant_id =restaurant.id))
    else:
        return render_template('deleteMenuItem.html',restaurant=restaurant,item=item)

#create api endpoint for /restaurants/JSON
@app.route('/restaurants/JSON/')
def showRestaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants = [restaurant.serialize for restaurant in restaurants])

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):
    # restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems = [item.serialize for item in items])
    
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def showMenuItemJSON(restaurant_id,menu_id):
    # restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem = item.serialize)


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
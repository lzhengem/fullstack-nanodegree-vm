from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem #importing from our database_setup.py file



engine = create_engine('sqlite:///restaurantmenu.db') #lets program know which database engine we want to communicate with
Base.metadata.bind = engine #creates the connection between the db tables and our classes
DBSession = sessionmaker(bind = engine) #establishes a link of communcation between our code executions and the engine we created
#sessions allow us to write the commands we want to execute but not send them to the database until we call a commit
session = DBSession()
myFirstRestaurant = Restaurant(name = "Pizza Palace") #create a new restaurant object
session.add(myFirstRestaurant) #adds this new restaurant to the staging zone to be added to db
session.commit() #adds this restaurant to db
session.query(Restaurant).all() #get all the restaurants in the db
cheesepizza = MenuItem(name = "Cheese Pizza", description = "Made with all natural ingredients and fresh mozzarella",
    course = "Entree", price = "$8.99", restaurant = myFirstRestaurant)
session.add(cheesepizza)
session.commit()
session.query(MenuItem.all()) #get all the menuitems in the db
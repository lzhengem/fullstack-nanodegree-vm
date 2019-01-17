from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__) #create instance of flask, using the current name of running application as argument

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/') #decorator in python. this means that whenever we get a hit on / or /hello, the HelloWorld() function gets invoked
@app.route('/hello')
def HelloWorld():
    restaurant = session.query(Restaurant).first()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    
    return "Hello World" #writes out hello world to the browser

if __name__ == '__main__': #application run by the Python interpreter gets a name 
# variable set to __main__, whereas all other imported python files get a __name__ set to the actual name of the python file
                            #this makes sure that this code only gets run if it is run from the python interpreter, not as an imported module 
    app.debug = True    #this allows you not to have to restart your server everytime you edit soemthing
    app.run(host='0.0.0.0', port=5000) #makes vagrant to listen to all public ip addresses
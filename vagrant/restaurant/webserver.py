from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi #common gateway interface used to decipher message sent from server
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "Hello!"
                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output +="&#161Hola! <a href='/hello'>Back to  Hello</a>"
                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('content-type','text/html')
                self.end_headers()

                output = "<a href='/restaurants/new'>Make new restaurant</a></br>"
                output += "<html><body>"
                restaurants = session.query(Restaurant).all()
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "</br>"
                    output += "<a href=/restaurants/%s/edit>Edit</a>" % restaurant.id
                    output += "</br>"
                    output += "<a href=/restaurants/%s/delete>Delete</a>" %restaurant.id
                    output += "<br></br>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('content-type','text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='newRestaurantName' type='text' placeholder = 'New Retaurant Name'>"
                output += "<input type='submit' value='Create'>"
                output += "</form>"
                output += "</body></html>"

                self.wfile.write(output)

            if self.path.endswith("/edit"):
                restaurantId = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantId).one_or_none() 
                output = ""
                if restaurant: #if there is a restaurant that gets returned
                    self.send_response(200)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    output += "<html><body>"
                    output += "<h1>Edit restaurant name for %s</h1>" % restaurant.name
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restaurantId
                    output += "<input type='text' name='newRestaurantName' placeholder='%s'>" % restaurant.name
                    output += "<input type='submit' value='Update'>"
                    output += "</form>"
                    output += "</body></html>"
                    
                else:
                    self.send_response(404)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    output = "that restaurant is not found"
                self.wfile.write(output)

            if self.path.endswith("/delete"):
                restaurantId = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantId).one()
                if restaurant:
                    self.send_response(200)
                    self.send_header('content-type','text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "Are you sure you want to delete?</br>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" %restaurantId
                    output += "<input type='submit' value='Delete'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output)



                


        except IOError:
            self.send_error(404, "File not Found %s" % self.path)

    def do_POST(self):
        try:
            # self.send_response(301)
            # self.end_headers()

            # ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            # if ctype == 'multipart/form-data':
            # 	fields=cgi.parse_multipart(self.rfile, pdict)
            	# messagecontent = fields.get('message')
            # output = ""
            # output += "<html><body>"
            # output += "<h2> Okay, how about this: </h2>"
            # output += "<h1>%s</h1>" % messagecontent[0]
            # output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
            # output+="</body></html>"
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    restaurantName = fields.get('newRestaurantName')
                    newRestaurant = Restaurant(name = restaurantName[0])
                    session.add(newRestaurant)
                    session.commit()
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    newRestaurantName = fields.get('newRestaurantName')
                    restaurantId = self.path.split("/")[2]
                    restaurant = session.query(Restaurant).filter_by(id=restaurantId).one_or_none()         
                    if restaurant and newRestaurantName: #if the restaurant exists and user entered a newRestaurantName, change it
                        restaurant.name = newRestaurantName[0]
                        session.add(restaurant)
                        session.commit()

                        self.send_response(301)
                        self.send_header('content-type','text/html')
                        self.send_header('Location','/restaurants/%s/edit' % restaurantId)
                        self.end_headers()

            if self.path.endswith("/delete"):
            
                restaurantId = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantId).one()
                if restaurant:
                    session.delete(restaurant)
                    session.commit()
                    print "deleted"

                    self.send_response(301)
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever() #keep server listening on port 8080 until ctrl+c

    except KeyboardInterrupt: #triggered if user clicks on ctrl+c,
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
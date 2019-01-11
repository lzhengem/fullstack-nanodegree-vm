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
                    output += "<a href=#>Edit</a>"
                    output += "</br>"
                    output += "<a href=#>Delete</a>"
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
from flask import flask
app = Flask(__name__)

if name == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
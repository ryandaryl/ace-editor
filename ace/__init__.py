import os
from flask import Flask, send_from_directory
from whitenoise import WhiteNoise

app = Flask(__name__)

# Use this app to serve static files.
wnapp = WhiteNoise(app, root='./ace/public/')

@app.route('/')
def index():
    return send_from_directory(os.getcwd() + '/ace/public', 'index.html')
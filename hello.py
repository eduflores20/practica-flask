from flask import Flask 
from flask import render_template

app = Flask(__name__)

@app.route("/")
def index():
    return 'Index Page'

@app.route("/code")
def code():
    return "El código en casa"


import os
from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

PASSWORD = os.environ.get('MONGO_PASS', None)
connection = MongoClient("ds047458.mongolab.com", 47458)
db = connection["movlistr"]
db.authenticate("dosh", str(PASSWORD))

@app.route('/')
def index():
	return 'Hello World'

if __name__ == "__main__":
	app.run(host='0.0.0.0')

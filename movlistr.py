import os
from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

UNAME = 'dosh'
PASSWORD = os.environ.get('MONGO_PASS', None)
URI = 'mongodb://' + UNAME + ':' + str(PASSWORD) + '@ds047458.mongolab.com:47458/movlistr'
print URI
client = MongoClient('URI')
db = MongoClient.movlistr

@app.route('/')
def index():
	return 'Hello World'

if __name__ == "__main__":
	app.run(host='0.0.0.0')

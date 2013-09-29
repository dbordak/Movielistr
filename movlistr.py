#!/usr/bin/python2

import os
from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

UNAME = os.environ.get('MONGO_UNAME', None)
PORT = os.environ.get('MONGO_PORT', None)
PASSWORD = os.environ.get('MONGO_PASS', None)
connection = MongoClient("ds0"+str(PORT)+".mongolab.com", int(PORT))
db = connection["movlistrdev"]
db.authenticate(str(UNAME), str(PASSWORD))

@app.route('/')
def index():
	return 'Hello World'

@app.route('/g/<group>')
def viewGroup(group):
	grp=db[group]
	#ret = ''
	#for post in grp.find():
	#	ret = ret + str(post)
	#return ret

	return render_template('list.html', posts=grp.find())

if __name__ == "__main__":
	app.run(host='0.0.0.0')

def search(peepArray,group):
	peepString = ""
	for peep in peepArray:
		peepString = peepString + peep + " "
	return db.command('text',group,search=peepString,limit=10)['results']

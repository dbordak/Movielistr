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
	p = [ "Bonk", "Boink" ]
	createGroup("Scoot",p,"Pootisman 2",p)
	return 'Hello World'

@app.route('/g/<group>')
def viewGroup(group):
	if group.startswith("NAMES"):
		return "nope"
	if group.startswith("system"):
		return "nope"
	if group.startswith("objectlabs"):
		return "nope"
	grp=db[group]
	nam=db["NAMES"+group]
	#ret = ''
	#for post in grp.find():
	#	ret = ret + str(post)
	#return ret

	return render_template('list.html', posts=grp.find())

if __name__ == "__main__":
	app.run(host='0.0.0.0')

# Returns a JSON array whose elements contain the fields "score" and "obj".
# After the search is completed, "score" is no longer needed -- in order to
# use the results, you should iterate through the array and use the "obj"s,
# which contain the usual _id, title, and peeps fields.
def search(group,peepArray):
	peepString = ""
	for peep in peepArray:
		peepString = peepString + peep + " "
	return db.command('text',group,search=peepString,limit=10)['results']

# The following 3 functions are untested.

# Mongo won't actually create a collection unless there's an element, so
# force users to add one movie in order to create their group.
def createGroup(groupName,peepArray,title,subPeepArray):
	nam=db["NAMES"+groupName]
	nam.insert({"names":peepArray})
	addMovie(groupName,title,subPeepArray)
	db[groupName].create_index([('peeps','text')])

def addMovie(groupName,title,peepArray):
	grp=db[groupName]
	grp.insert( {
		"title" : title,
		"peeps" : peepArray
		} )

def updatePeeps(groupName,idnum,peepArray):
	grp=db[groupName]
	if len(peepArray):
		grp.update( { "_id" : idnum }, { "$set" : { "peeps" : peepArray } } )
	else:
		grp.remove( { "_id" : idnum } )

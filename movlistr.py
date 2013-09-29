#!/usr/bin/python2

import os
from flask import Flask, render_template, request
from pymongo import MongoClient
from urllib2 import urlopen
from json import loads

app = Flask(__name__)

UNAME = os.environ.get('MONGO_UNAME', None)
PORT = os.environ.get('MONGO_PORT', None)
PASSWORD = os.environ.get('MONGO_PASS', None)
NYT_API_KEY = os.environ.get('NYT_API_KEY', None)
NYT_BASE_URL = "http://api.nytimes.com/svc/movies/v2/reviews/search?"

MAX_RECOMMENDATIONS = 3

connection = MongoClient("ds0"+str(PORT)+".mongolab.com", int(PORT))
db = connection["movlistrdev"]
db.authenticate(str(UNAME), str(PASSWORD))

def create_nyt_url(searchTerm):
	searchTerm = searchTerm.replace(' ','+')
	return NYT_BASE_URL+"&query='"+searchTerm+"'&api-key="+NYT_API_KEY

def get_json(URL):
	return loads(urlopen(URL).read())

# Returns a JSON array whose elements contain the fields "score" and "obj".
# After the search is completed, "score" is no longer needed -- in order to
# use the results, you should iterate through the array and use the "obj"s,
# which contain the usual _id, title, and peeps fields.
def search(group,peepString):
	peepString.replace(","," ")
	return db.command('text',group,search=peepString,limit=MAX_RECOMMENDATIONS)['results']

# Returns a json with Title, Peeps, Summary, and a link to the NYT review
def makeResultsJson(Jason):
	movies = []
	for movie in Jason:
		m = movie['obj']
		print "I got to here"
		#URL = create_nyt_url(movie['obj']['title'])
		#print URL
		#j = get_json(URL)
		#m['summary'] = j['capsule_review']
		#m['link'] = j['link']['url']
		movies.append(m)

def getResults(group,peepString):
	print "test"
	return makeResultsJson(search(group,peepString))

# Mongo won't actually create a collection unless there's an element, so
# force users to add one movie in order to create their group.
def createGroup(groupName, peepString, title, subPeepArray):
	peepArray = peepString.split()
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

def updateFromString(groupName,title,peepString):
	peepArray = peepString.split(',')
	updatePeeps(groupName,title,peepArray)

def updatePeeps(groupName,title,peepArray):
	grp=db[groupName]
	if len(peepArray):	
		newEntry = {
				"title" : title,
				"peeps" : peepArray
				}
		grp.find_and_modify(
				query={ "title" : title },
				update=newEntry
				)
	else:
		grp.remove( { "title" : title } )

@app.route('/')
def index():
	return 'Hello World'

@app.route('/g/<group>', methods=['GET', 'POST'])
def viewGroup(group):
	if group.startswith("NAMES"):
		return "nope"
	if group.startswith("system"):
		return "nope"
	if group.startswith("objectlabs"):
		return "nope"
	if request.method == 'GET':
		grp=db[group]
		nam=db["NAMES"+group]

		return render_template('list.html', posts=grp.find(), names=nam.find_one()['names'])
	if request.method == 'POST':
		updateFromString(group, request.form['title'], request.form['data'])
		return 'good'

@app.route('/g/<group>/s', methods=['POST'])
def searchRoute(group):
	#return str(request.form['data'])
	print "Before calling getResults"
	return getResults(group, request.form['data'])


if __name__ == "__main__":
	app.debug = True
	app.run()
	#app.run(host='0.0.0.0')


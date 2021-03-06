#!/usr/bin/python2

import os
from flask import Flask, render_template, request
from pymongo import MongoClient
from urllib2 import urlopen
from json import loads
import string

app = Flask(__name__)

UNAME = os.environ.get('MONGO_UNAME', None)
PORT = os.environ.get('MONGO_PORT', None)
PASSWORD = os.environ.get('MONGO_PASS', None)
NYT_API_KEY = os.environ.get('NYT_API_KEY', None)
NYT_BASE_URL = "http://api.nytimes.com/svc/movies/v2/reviews/search?"

MAX_RECOMMENDATIONS = 4

connection = MongoClient("ds0"+str(PORT)+".mongolab.com", int(PORT))
db = connection["movlistrdev"]
db.authenticate(str(UNAME), str(PASSWORD))

def create_nyt_url(searchTerm,exact):
	searchTerm = searchTerm.replace(' ','+')
	if exact:
		return NYT_BASE_URL+"&query='"+searchTerm+"'&api-key="+NYT_API_KEY
	else:
		return NYT_BASE_URL+"&query="+searchTerm+"&api-key="+NYT_API_KEY

def get_json(URL):
	return loads(urlopen(URL).read())

def cleanTextRes(Jason):
	movies = []
	for m in Jason:
		movie = m['obj']
		movies.append(movie)
	return movies

# Returns a JSON array whose elements contain the fields "score" and "obj".
# After the search is completed, "score" is no longer needed -- in order to
# use the results, you should iterate through the array and use the "obj"s,
# which contain the usual _id, title, and peeps fields.
def textSearch(group,peepString):
	return db.command('text',group,search=peepString,limit=MAX_RECOMMENDATIONS)['results']

def search(group,peepString):
	grp = db[group]
	peepString = peepString.replace(","," ")
	peepArray = peepString.split()
	set1 = []
	set2 = []
	for doc in grp.find({ "peeps" : { "$all": peepArray } }).sort("numPeeps").limit(MAX_RECOMMENDATIONS):
		set1.append(doc)
	for doc in grp.find({ "peeps" : { "$in": peepArray } }).sort("numPeeps").limit(MAX_RECOMMENDATIONS):
		set2.append(doc)
	if len(set1):
		for doc in set2:
			if doc not in set1:
				set1.append(doc)
		return set1
	else:
		set1 = cleanTextRes(textSearch(group,peepString))
		set1.extend(set2)
		return set1

def get_NYT_stuff(title):
	URL = create_nyt_url(title,True)
	j = get_json(URL)
	if int(j['num_results']):
		return {
				"summary" : j['results'][0]['capsule_review'],
				"link" : j['results'][0]['link']['url']
				}
	else:
		return {
				"summary" : "No summary found",
				"link" : "No link found"
				}

def simpleCreateGroup(groupName, peepString):
	peepString = peepString.replace(","," ")
	title = "Star Wars Holiday Special"
	subPeepArray = peepString.split()
	createGroup(groupName,peepString,title,subPeepArray)

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
	n = get_NYT_stuff(title)
	grp.insert( {
		"title" : title,
		"peeps" : peepArray,
		"numPeeps" : len(peepArray),
		"summary" : n['summary'],
		"link" : n['link']
		} )

def updateFromString(groupName,title,peepString):
	peepArray = peepString.split(',')
	updatePeeps(groupName,title,peepArray)

def updatePeeps(groupName,title,peepArray):
	grp=db[groupName]
	if len(peepArray)==1:
		if len(peepArray[0])==0:
			grp.remove( { "title" : title } )
	elif len(peepArray):	
		newEntry = {
				"title" : title,
				"peeps" : peepArray,
				"numPeeps" : len(peepArray)
				}
		grp.find_and_modify(
				query={ "title" : title },
				update=newEntry
				)
	else:
		grp.remove( { "title" : title } )

@app.route('/')
def index():
	return render_template('list.html')

@app.route('/g/<group>', methods=['GET', 'POST'])
def viewGroup(group):
	if group.startswith("NAMES"):
		return "Group cannot start with 'NAMES'"
	if group.startswith("system"):
		return "Group cannot start with 'system'"
	if group.startswith("objectlabs"):
		return "Group cannot start with 'objectlabs'"
	if request.method == 'GET':
		grp=db[group]
		nam=db["NAMES"+group]

		return render_template('list.html', posts=grp.find(), names=nam.find_one()['names'])
	if request.method == 'POST':
		updateFromString(group, request.form['title'], request.form['data'])
		return 'good'

@app.route('/c/<group>', methods=['GET', 'POST'])
def addGroup(group):
	simpleCreateGroup(string.lower(group),request.form['data'])
	return 'good'

def jsonToStringThing(Jason):
	movString = ""
	for m in Jason:
		peepString = ""
		for peep in m['peeps']:
			peepString = peepString + peep + " "
		peepString.strip()
		movString = movString + m['title'] + " needs to be seen by " + peepString + ".\n" #+ '"' + m['summary'] + '"' + "\n" + "New York Times Review at: " + m['link'] + "\n\n"
	return movString

@app.route('/g/<group>/s', methods=['POST'])
def searchRoute(group):
	resultJson = search(group, request.form['data'])
	#return jsonToStringThing(resultJson)
	return render_template('results.html', data = resultJson)


if __name__ == "__main__":
	app.debug = True
	app.run()
	#app.run(host='0.0.0.0')

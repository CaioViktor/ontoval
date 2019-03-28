import os
from flask import Flask,render_template,request, redirect, url_for
import ontology
import pymongo


NAME_DB = "ontoval"
ONTO_COLL = "ontologies"


mongo = pymongo.MongoClient("mongodb://localhost:27017/")


db = mongo[NAME_DB]
onto_coll = db[ONTO_COLL]
onto_coll.insert_one({'id':'-1'})
onto_coll.delete_one({'id':'-1'})


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/ontologies"

@app.route("/")
def index():
	ontologies = []
	cur = onto_coll.find()
	for ontology in cur:
		ontologies.append(ontology)
	return render_template("index.html",ontologies=ontologies)

if __name__ == "__main__":
	app.run(host='0.0.0.0')
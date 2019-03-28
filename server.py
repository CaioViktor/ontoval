import os
from flask import Flask,render_template,request, redirect, url_for
import ontology as ont
import pymongo


NAME_DB = "ontoval"
CONFIG_COLL = "config"
ONTO_COLL = "ontologies"


mongo = pymongo.MongoClient("mongodb://localhost:27017/")


db = mongo[NAME_DB]
onto_coll = db[ONTO_COLL]
onto_coll.insert_one({'id':'-1'})
onto_coll.delete_one({'id':'-1'})

config_coll = db[CONFIG_COLL]

if config_coll.find_one() is None:
	config_coll.insert_one({"id_ontology":1})

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/ontologies"

@app.route("/")
def index():
	ontologies = []
	cur = onto_coll.find()
	for ontology in cur:
		ontologies.append(ontology)
	return render_template("index.html",ontologies=ontologies)


@app.route("/new")
def new():
	return render_template("new.html")

@app.route("/newConfirm",methods=['POST'])
def newConfirm():
	id_ontology = (config_coll.find_one())['id_ontology']
	ontologia = {"id":id_ontology,"name":request.form['nome'],"descrition":request.form['descricao'],"file":"","image":"","qtd_classes":0,"qtd_properties":0,"qtd_evaluations":0,"classes":{},"properties":{},"evaluations":{}} 

	ontologia_file = request.files['ontologia']
	ext_ontologia = ontologia_file.filename.split(".")[1]
	ontologia_file_name = str(id_ontology)+"."+ext_ontologia
	ontologia_file_path = os.path.join(app.config['UPLOAD_FOLDER'],ontologia_file_name)
	ontologia_file.save(os.path.join(ontologia_file_path))
	ontologia["file"] = ontologia_file_path

	if "foto" in request.files:
		foto_file = request.files['foto']
		ext_foto = foto_file.filename.split(".")[1]
		foto_file_name = str(id_ontology)+"."+ext_foto
		foto_file_path = os.path.join(app.config['UPLOAD_FOLDER'],foto_file_name)
		foto_file.save(foto_file_path)
		ontologia["image"] = foto_file_path

	g = ont.getGraph(ontologia_file_path,ext_ontologia)

	classes = ont.getClasses(g)
	properties = ont.getProperties(g)

	ontologia['classes'] = classes
	ontologia['qtd_classes'] = len(classes)
	
	ontologia["properties"] = properties
	ontologia['qtd_properties'] = len(properties)

	onto_coll.insert_one(ontologia)
	config_coll.update_many({},{'$set':{'id_ontology':id_ontology+1}})


	return redirect(url_for("index"))

if __name__ == "__main__":
	app.run(host='0.0.0.0')
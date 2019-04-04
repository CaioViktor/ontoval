import os
from flask import Flask,render_template,request, redirect, url_for
import ontology as ont
import pymongo
import json
from ast import literal_eval
import time
import datetime
import dataAnalyses as da



NAME_DB = "ontoval"
CONFIG_COLL = "config"
ONTO_COLL = "ontologies"
EVAL_COLL = "evaluations"


mongo = pymongo.MongoClient("mongodb://localhost:27017/")


db = mongo[NAME_DB]

onto_coll = db[ONTO_COLL]
onto_coll.insert_one({'id':'-1'})
onto_coll.delete_one({'id':'-1'})

eval_coll = db[EVAL_COLL]
eval_coll.insert_one({'id':'-1'})
eval_coll.delete_one({'id':'-1'})

config_coll = db[CONFIG_COLL]

if config_coll.find_one() is None:
	config_coll.insert_one({"id_ontology":1})

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/ontologies"
app.config['JSON_FOLDER'] = "static/js"

@app.route("/")
def index():
	ontologies = []
	cur = onto_coll.find({},{"evaluations":0,"classes": 0,"properties": 0})
	for ontology in cur:
		ontologies.append(ontology)
	return render_template("index.html",ontologies=ontologies)


@app.route("/new")
def new():
	return render_template("new.html")

@app.route("/newConfirm",methods=['POST'])
def newConfirm():
	id_ontology = (config_coll.find_one())['id_ontology']
	ontologia = {"id":id_ontology,"name":request.form['nome'],"description":request.form['descricao'],"file":"","image":"","qtd_classes":0,"qtd_properties":0,"qtd_evaluations":0,"classes":{},"properties":{}} 

	ontologia_file = request.files['ontologia']
	ext_ontologia = ontologia_file.filename.split(".")[1]
	ontologia_file_name = str(id_ontology)+"."+ext_ontologia
	ontologia_file_path = os.path.join(app.config['UPLOAD_FOLDER'],ontologia_file_name)
	ontologia_file.save(ontologia_file_path)
	ontologia["file"] = ontologia_file_path

	if "foto" in request.files and request.files['foto'].filename != '':
		#print(request.files['foto'].filename)
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

@app.route("/eval/<ontology_id>/")
def eval_user(ontology_id):
	ontology_id = int(ontology_id)
	ontologia = onto_coll.find_one({'id':ontology_id},{'id':1,'name':1,'description':1})
	#eval_coll.insert_one(evaluation)
	
	return render_template("eval_user.html",ontology = ontologia)

@app.route("/eval/<ontology_id>/confirm",methods=['POST'])
def eval_user_confirm(ontology_id):
	ontology_id = int(ontology_id)
	evaluations = eval_coll.find({'ontology_id':ontology_id}).count()
	eval_id = int(evaluations) + 1
	evaluation = {'eval_id':eval_id,'ontology_id':ontology_id,'name':request.form['nameE'],'age':int(request.form['age']),'expert_domain':int(request.form['expert_domain']),'expert_ontology':int(request.form['expert_ontology']),'classes':[],'properties':[],'general':[],'completed':False,'timeStart':time.time(),'timeFinish':None}



	#print(evaluation)
	eval_coll.insert_one(evaluation)

	return redirect(url_for("eval",ontology_id=ontology_id,user=eval_id))


@app.route("/eval/<ontology_id>/<user>/")
def eval(ontology_id,user):
	ontology_id = int(ontology_id)
	ontologia = onto_coll.find_one({'id':ontology_id})

	#print(ontologia['properties'])

	user = int(user)	
	avaliacao = eval_coll.find_one({'eval_id': user,'ontology_id':ontology_id})

	if avaliacao['completed'] :
		return redirect(url_for("done"))

	status = 0 #falta avaliar classes
	indice = len(avaliacao['classes'])
	termo = {}

	if len(avaliacao['classes']) >= ontologia['qtd_classes']:
		if len(avaliacao['properties']) >= ontologia['qtd_properties']:
			if len(avaliacao['general']) >= 1:
				status = 1 #concluido
				return redirect(url_for("done"))
			else:
				status = 2 #falta avaliacao geral
				indice = 0
		else:
			status = 3 #falta avaliar propriedades
			indice = len(avaliacao['properties'])
			print(indice)
			termo = ontologia['properties'][list(ontologia['properties'])[indice]]
	else:
		termo = ontologia['classes'][list(ontologia['classes'])[indice]]

	indices = {'classes':[len(avaliacao['classes']),ontologia['qtd_classes']],'properties':[len(avaliacao['properties']),ontologia['qtd_properties']],'general':[len(avaliacao['general']),1]}

	questoes = json.load(open(os.path.join(app.config['JSON_FOLDER'],"questions.json"), encoding='utf-8'))
	return render_template("eval.html",status=status,ontologia=ontologia,questions=questoes,termo=termo,indices=indices,user=user)

@app.route("/eval/<ontology_id>/<user>/confirm",methods=['POST'])
def eval_confirm(ontology_id,user):
	ontology_id = int(ontology_id)
	user = int(user)
	#print("1")
	termo = literal_eval(request.form['termo'])
	#print("1.5")
	status = int(request.form['status'])
	#print("2")
	avaliacao = eval_coll.find_one({'eval_id': user,'ontology_id':ontology_id})
	#print("3")
	evaluation_termo = {'score':0,'observation':request.form['observation']}

	score_total = 0;
	score_reached = 0;

	if status == 0: #Classe
		#print("3.1")
		evaluation_termo['id'] = termo['id']
		evaluation_termo['c1'] = int(request.form['c1'])
		evaluation_termo['c2'] = int(request.form['c2'])
		evaluation_termo['c3'] = int(request.form['c3'])
		evaluation_termo['score_parents'] = 0
		evaluation_termo['score_dataProperties'] = 0
		evaluation_termo['score_objectProperties'] = 0

		score_total = 3
		score_reached = evaluation_termo['c1'] + evaluation_termo['c2'] + evaluation_termo['c3']

		evaluation_termo['parents'] = []
		for parent in termo['mae']:
			evaluation_termo['parents'].append([parent,int(request.form['m'+parent])])
			score_total = score_total + 1
			score_reached = score_reached + int(request.form['m'+parent])
			evaluation_termo['score_parents'] = evaluation_termo['score_parents'] + (int(request.form['m'+parent])/len(termo['mae']))

		evaluation_termo['dataTypeProperties'] = []
		for dp in termo['dataTypeProperties']:
			evaluation_termo['dataTypeProperties'].append([dp,int(request.form['a'+dp])])
			score_total = score_total + 1
			score_reached = score_reached + int(request.form['a'+dp])
			evaluation_termo['score_dataProperties'] = evaluation_termo['score_dataProperties'] + (int(request.form['a'+dp])/len(termo['dataTypeProperties']))

		evaluation_termo['objectProperties'] = []
		for op in termo['objectProperties']:
			evaluation_termo['objectProperties'].append([op,int(request.form['r'+op])])
			score_total = score_total + 1
			score_reached = score_reached + int(request.form['r'+op])
			evaluation_termo['score_objectProperties'] = evaluation_termo['score_objectProperties'] + (int(request.form['r'+op])/len(termo['objectProperties']))

		evaluation_termo['score'] = score_reached/score_total

		avaliacao['classes'].append(evaluation_termo)
	elif status == 3: #Propriedade
		#print("3.2")

		evaluation_termo['id'] = termo['id']
		evaluation_termo['p1'] = int(request.form['p1'])
		evaluation_termo['p2'] = int(request.form['p2'])
		evaluation_termo['p3'] = int(request.form['p3'])
		evaluation_termo['p5'] = int(request.form['p5'])
		evaluation_termo['score_parents'] = 0
		evaluation_termo['score_range'] = 0

		score_total = 4
		score_reached = evaluation_termo['p1'] + evaluation_termo['p2'] + evaluation_termo['p3'] + evaluation_termo['p5']
		#print("3.2.1")
		evaluation_termo['parents'] = []
		for parent in termo['mae']:
			evaluation_termo['parents'].append([parent,int(request.form['m'+parent])])
			score_total = score_total + 1
			score_reached = score_reached + int(request.form['m'+parent])
			evaluation_termo['score_parents'] = evaluation_termo['score_parents'] + (int(request.form['m'+parent])/len(termo['mae']))
		#print("3.2.2")
		evaluation_termo['range'] = []
		for dp in termo['range']:
			nameC = 'r'+dp
			#print("3.2.2.1")
			if termo['type'] == 'owl:DatatypeProperty':
				#print("Entrou")
				nameC= 'r'+ dp.replace(".","").replace("/","").replace(":","").replace("#","")
			#print("3.2.2.2")
			#print(nameC)
			evaluation_termo['range'].append([dp,int(request.form[nameC])])
			#print("3.2.2.3")
			score_total = score_total + 1
			score_reached = score_reached + int(request.form[nameC])
			#print("3.2.2.4")
			evaluation_termo['score_range'] = evaluation_termo['score_range'] + (int(request.form[nameC])/len(termo['range']))


		#print("3.2.3")
		evaluation_termo['score'] = score_reached/score_total
		#print(avaliacao)
		avaliacao['properties'].append(evaluation_termo)
		#return render_template("print.html",mensagem=avaliacao)


	elif status == 2: #Geral
		#print("3.3")
		evaluation_termo['g1'] = int(request.form['g1'])
		evaluation_termo['g2'] = int(request.form['g2'])
		evaluation_termo['g3'] = int(request.form['g3'])
		evaluation_termo['g4'] = int(request.form['g4'])
		evaluation_termo['g5'] = int(request.form['g5'])
		evaluation_termo['g6'] = int(request.form['g6'])
		evaluation_termo['score']= (evaluation_termo['g1'] + evaluation_termo['g2'] + evaluation_termo['g3'] + evaluation_termo['g4'] + evaluation_termo['g5'] + evaluation_termo['g6'])/6
		
		avaliacao['general'].append(evaluation_termo)
		avaliacao['completed'] = True
		avaliacao['timeFinish'] = time.time()
		print("Tempo: " + str(datetime.timedelta(seconds=(avaliacao['timeFinish']-avaliacao['timeStart']))))

		eval_coll.replace_one({'eval_id': user,'ontology_id':ontology_id},avaliacao)
		ontologia = onto_coll.find_one({'id':ontology_id},{'qtd_evaluations':1})
		qtd = ontologia['qtd_evaluations'] +1
		onto_coll.update_one({'id':ontology_id},{'$set':{'qtd_evaluations':qtd}})

		return redirect(url_for("done"))
	#print("4")
	eval_coll.replace_one({'eval_id': user,'ontology_id':ontology_id},avaliacao)
	return redirect(url_for("eval",ontology_id=ontology_id,user=user))
	#return render_template("print.html",mensagem=avaliacao)
@app.route("/done")
def done():
	return render_template("done.html")

@app.route("/eval/<ontology_id>/<user>/back")
def back(ontology_id,user):
	ontology_id = int(ontology_id)
	user = int(user)
	avaliacao = eval_coll.find_one({'eval_id': user,'ontology_id':ontology_id})

	if len(avaliacao['general']) > 0 :
		avaliacao['general'].pop()
		eval_coll.update_one({'eval_id': user,'ontology_id':ontology_id},{'$set':{'general':avaliacao['general']}})
	elif len(avaliacao['properties']) > 0 :
		avaliacao['properties'].pop()
		eval_coll.update_one({'eval_id': user,'ontology_id':ontology_id},{'$set':{'properties':avaliacao['properties']}})
	elif len(avaliacao['classes']) > 0 :
		avaliacao['classes'].pop()
		eval_coll.update_one({'eval_id': user,'ontology_id':ontology_id},{'$set':{'classes':avaliacao['classes']}})
	return redirect(url_for("eval",ontology_id=ontology_id,user=user))

@app.route("/analize/<ontology_id>/")
def result(ontology_id):
	ontology_id = int(ontology_id)
	cursor = eval_coll.find({'ontology_id':ontology_id,'completed':True})
	evaluations = da.getDataFrameGeneral(cursor)

	cursor = onto_coll.find_one({'id':ontology_id},{'name':1,'classes':1,'properties':1})
	classes = {}
	properties = {}
	for classe in cursor['classes']:
		classes[classe] = cursor['classes'][classe]['uri']

	for propertie in cursor['properties']:
		properties[propertie] = cursor['properties'][propertie]['uri']

	evaluations['score_classe'] = evaluations.loc[:,list(map(lambda idx: 's'+idx,classes.keys()))].T.mean()
	evaluations['score_properties'] = evaluations.loc[:,list(map(lambda idx: 's'+idx,properties.keys()))].T.mean()

	#evaluations.plot(x='expert_domain',y='score_classes',kind='scatter',title='dominio X score classes').get_figure()
	return render_template('result.html',name=cursor['name'],evaluations=evaluations,classes=classes,properties=properties,generalClasses=evaluations['score_classe'],generalProperties=evaluations['score_properties'])

if __name__ == "__main__":
	#app.run(host='200.19.182.252')
	app.run(host='0.0.0.0')
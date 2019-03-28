from rdflib import Graph
import os
import hashlib

path = os.path.abspath("C:/Users/CaioV/Programacao/ontologia.owl")
g = Graph()
g.parse(path,format="ttl")
def getClasses(g):
	query = """
	    PREFIX dc: <http://purl.org/dc/elements/1.1/>
	    
	    SELECT DISTINCT ?classe (str(?title) as ?title) (str(?comment) as ?comment) ?objectOp ?dataOp ?mae WHERE{
	        {?classe rdf:type owl:Class.}
	        UNION
	        {?classe rdf:type rdfs:Class.}
	        OPTIONAL{
	            ?classe rdfs:subClassOf ?mae.
	        }
	        OPTIONAL{
	            {?classe rdfs:label ?title.}
	            UNION
	            {?classe dc:title ?title.}
	        }
	        OPTIONAL{
	            ?classe rdfs:comment ?comment
	        }
	        OPTIONAL {
	            ?objectOp rdf:type owl:ObjectProperty;
	                rdfs:domain ?classe
	        }
	        
	        OPTIONAL {
	            ?dataOp rdf:type owl:DatatypeProperty;
	                rdfs:domain ?classe
	        }
	    }
	"""

	result = g.query(query)

	classes = {}

	for row in result:
		id_hash = hashlib.md5(str(row["classe"]).encode('utf-8')).hexdigest()
		classe = {'id':id_hash,'uri':row["classe"].n3(),'labels':[],'comments':[],'dataTypeProperties':[],'objectProperties':[],'mae':[]}

		if id_hash in classes:
		    classe = classes[id_hash]

		if str(row["title"]) not in classe['labels'] and str(row["title"]) != "None":
		    classe['labels'].append(str(row["title"]))

		if str(row["comment"]) not in classe['comments'] and str(row["comment"]) != "None":
		    classe['comments'].append(str(row["comment"]))
		    

		if str(row["dataOp"]) != "None":
		    dp_hash = hashlib.md5(str(row["dataOp"]).encode('utf-8')).hexdigest()
		    if dp_hash not in classe['dataTypeProperties']:
		        classe['dataTypeProperties'].append(dp_hash)
		        
		if str(row["objectOp"]) != "None":
		    ob_hash = hashlib.md5(str(row["objectOp"]).encode('utf-8')).hexdigest()
		    if ob_hash not in classe['objectProperties']:
		        classe['objectProperties'].append(ob_hash)

		if str(row["mae"]) != "None":
		    mae_hash = hashlib.md5(str(row["mae"]).encode('utf-8')).hexdigest()
		    if mae_hash not in classe['mae']:
		        classe['mae'].append(mae_hash)

		classes[id_hash] = classe

	return classes

def getProperties(g):
	query = """
	    PREFIX dc: <http://purl.org/dc/elements/1.1/>
	    
	    SELECT DISTINCT ?propriedade ?tipo (str(?title) as ?title) (str(?comment) as ?comment) ?domain ?range ?mae WHERE{
	        {
	            ?propriedade rdf:type rdf:Property
	            BIND("rdf:Property" as ?tipo)
	        }
	        UNION{
	            ?propriedade rdf:type owl:ObjectProperty
	            BIND("owl:ObjectProperty" as ?tipo)
	        }
	        UNION{
	            ?propriedade rdf:type owl:DatatypeProperty;
	            BIND("owl:DatatypeProperty" as ?tipo)
	        }
	        OPTIONAL{
	            {?propriedade rdfs:label ?title.}
	            UNION
	            {?propriedade dc:title ?title.}
	        }
	        OPTIONAL{
	            ?propriedade rdfs:comment ?comment
	        }
	        OPTIONAL{
	            ?propriedade rdfs:domain ?domain
	        }
	        OPTIONAL{
	            ?propriedade rdfs:range ?range
	        }
	        OPTIONAL{
	            ?propriedade rdfs:subPropertyOf ?mae.
	        }
	    }
	"""
	result = g.query(query)
	propriedades = {}
	for row in result:
		id_hash = hashlib.md5(str(row["propriedade"]).encode('utf-8')).hexdigest()
		propriedade = {'id':id_hash,'uri':row["propriedade"].n3(),'labels':[],'comments':[],'type':str(row['tipo']),'domain':[],'range':[],'mae':[]}

		if id_hash in propriedades:
		    propriedade = propriedades[id_hash]

		if str(row["title"]) not in propriedade['labels'] and str(row["title"]) != "None":
		    propriedade['labels'].append(str(row["title"]))

		if str(row["comment"]) not in propriedade['comments'] and str(row["comment"]) != "None":
		    propriedade['comments'].append(str(row["comment"]))
		    

		if str(row["domain"]) != "None":
		    domain_hash = hashlib.md5(str(row["domain"]).encode('utf-8')).hexdigest()
		    if domain_hash not in propriedade['domain']:
		        propriedade['domain'].append(domain_hash)
		        
		if str(row["range"]) != "None":
		    range_hash = hashlib.md5(str(row["range"]).encode('utf-8')).hexdigest()
		    if range_hash not in propriedade['range']:
		        propriedade['range'].append(range_hash)
		        
		if str(row["mae"]) != "None":
		    mae_hash = hashlib.md5(str(row["mae"]).encode('utf-8')).hexdigest()
		    if mae_hash not in propriedade['mae']:
		        propriedade['mae'].append(mae_hash)

		propriedades[id_hash] = propriedade

	return propriedades
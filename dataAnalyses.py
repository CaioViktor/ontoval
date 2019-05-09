import pandas as pd
def getDataFrameSummary_General(cursor):
	evals = []
	evalg = []
	for evalu in cursor:
		ev = {'id':evalu['eval_id'],'name':evalu['name'],'age':evalu['age'],'expert_domain':evalu['expert_domain'],'expert_ontology':evalu['expert_ontology'],'time':(evalu['timeFinish'] - evalu['timeStart'])}
		for classe in evalu['classes']:
			ev['s'+str(classe['id'])] = classe['score']
			ev['p'+str(classe['id'])] = classe['score_parents']
			ev['d'+str(classe['id'])] = classe['score_dataProperties']
			ev['o'+str(classe['id'])] = classe['score_objectProperties']
		for prop in evalu['properties']:
			ev['s'+str(prop['id'])] = prop['score']
			ev['p'+str(prop['id'])] = prop['score_parents']
			ev['r'+str(prop['id'])] = prop['score_range']

		evals.append(ev)

		evg = {'id':evalu['eval_id'],'g1': evalu['general'][0]['g1'], 'g2': evalu['general'][0]['g2'],'g3': evalu['general'][0]['g3'],'g4': evalu['general'][0]['g4'],'g5': evalu['general'][0]['g5'],'g6': evalu['general'][0]['g6']}	
		evalg.append(evg)
	return pd.DataFrame(evals),pd.DataFrame(evalg)


def getDataFrameClass(cursor,id_term):
	observations = []
	evals = []
	pt = set()
	op = set()
	dp = set()
	for evalu in cursor:
		classe = list(filter(lambda x: x['id'] == id_term,evalu['classes']))[0]
        
		ev = {'expert_domain':evalu['expert_domain'],'expert_ontology':evalu['expert_ontology'],'score' : classe['score'], 'c1' : classe['c1'],'c2' : classe['c2'],'c3' : classe['c3'],'score_parents':classe['score_parents'],'score_dataProperties':classe['score_dataProperties'],'score_objectProperties':classe['score_objectProperties']}

		for p in classe['parents']:
			ev[p[0]]=p[1]
			pt.add(p[0])

		for p in classe['dataTypeProperties']:
			ev[p[0]]=p[1]
			dp.add(p[0])
		    
		for p in classe['objectProperties']:
			ev[p[0]]=p[1]
			op.add(p[0])
		    
		if classe['observation'] != '':
			observations.append(classe['observation'])
		evals.append(ev)
	return pd.DataFrame(evals) , observations , list(pt) , list(op) , list(dp)


def getDataFrameProperties(cursor,id_term):
	observations = []
	evals = []
	pt = set()
	rp = set()
	for evalu in cursor:
		classe = list(filter(lambda x: x['id'] == id_term,evalu['properties']))[0]
        
		ev = {'expert_domain':evalu['expert_domain'],'expert_ontology':evalu['expert_ontology'],'score' : classe['score'], 'p1' : classe['p1'],'p2' : classe['p2'],'p3' : classe['p3'],'p5' : classe['p5'],'score_parents':classe['score_parents'],'score_range' : classe['score_range']}

		for p in classe['parents']:
			ev[p[0]]=p[1]
			pt.add(p[0])

		for p in classe['range']:
			ev[p[0]]=p[1]
			rp.add(p[0])
		    
	
		    
		if classe['observation'] != '':
			observations.append(classe['observation'])
		evals.append(ev)
	return pd.DataFrame(evals) , observations , list(pt) , list(rp)


def getURIs(cursor):
	uris = {}
	for classe in cursor['classes']:
		uris[classe] = cursor['classes'][classe]['uri']
	for propertie in cursor['properties']:
		uris[propertie] = cursor['properties'][propertie]['uri']
	return uris
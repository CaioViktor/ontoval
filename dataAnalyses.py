import pandas as pd
def getDataFrameGeneral(cursor):
	evals = []
	for evalu in cursor:
		ev = {'id':evalu['eval_id'],'name':evalu['name'],'age':evalu['age'],'expert_domain':evalu['expert_domain'],'expert_ontology':evalu['expert_ontology']}
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
	return pd.DataFrame(evals)
import os
import sys
import Core.DataImport.parse_data_cmds as parse_data_cmds
import Core.DataImport.import_data_class as import_data_class
from pyomo.environ import *
from pyomo.opt import SolverFactory
import itertools
from pyutilib.misc import Options
import time as timer
import pdb
import Core.scenario_class as scenario_class
import Core.Solvers.MSSP.defunction as defunction
import Core.Valuation as Valuation
import Core.Solvers.MTSSP.M2S_item as M2S_item
import gc
import random
#import resource

def Deterministic_PRDP_Solve(mipgap, model_data, output_directory):
	### Start Solution Timer
	start_time = timer.clock()
	#init_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

	##Solver Choice
	opt = SolverFactory("cplex")
	options = Options()
	opt.options.mip_tolerances_mipgap = mipgap
	
	
	##########################################
	### Generate Scenario
	##########################################
	
	#### Problem Info For Scenario Generation
	num_product = len(model_data._data['product'][None])
	prod = model_data._data['product'][None]
	
	num_trial = len(model_data._data['trial'][None])
	sg = model_data._data['trial'][None]
	
	prob = model_data._data['probability']
	num_ts = len(model_data._data['time_step'][None])
	
	### Generate all possible outcomes
	Outcomes = itertools.product(range(num_trial + 1), repeat = num_product)
	Outcomes = tuple(Outcomes)
	
	### From Outcomes Name and Generate Scenarios
	scenario = 1
	List_of_Scenarios = {}
	SS=[]
	
	for items in Outcomes:
		scenario_name = scenario
		List_of_Scenarios[scenario_name] = scenario_class.scenario(items,prob, prod,sg)
		SS.append(scenario_name)
		scenario += 1
	
	##########################################################
	### Input Parameters to Solver
	##########################################################
	
	rev_max = {}
	gammaL = {}
	gammaD = {}
	duration = {}
	trial_cost = {}
	revenue_max = {}
	success = {}
	rev_run = {}
	rev_open = {}
	discounting_factor ={}
	
	##Set product
	product = model_data._data['product'][None]
		
	##Set stage_gate
	stage_gate = model_data._data['trial'][None]
	
	## Set time step
	time_step = model_data._data['time_step'][None]
	
	##Set resource type
	resource_type = model_data._data['resource_type'][None]
	
	## Set duration
	duration = model_data._data['trial_duration']
	
	## Set trial cost
	trial_cost = model_data._data['trial_cost']
	
	## Set Discount Values
	for items in model_data._data['gammaL']:
		gammaL[items[0]] = model_data._data['gammaL'][items]
		
	for items in model_data._data['gammaD']:
		gammaD[items[0]] = model_data._data['gammaD'][items]
	
	## Set Maximum Revenue	
	for items in model_data._data['maximum_revenue']:
		revenue_max[items[0]] = model_data._data['maximum_revenue'][items]
		
	## Set Last Trial
	last_trial = len(stage_gate)
	
	last_time_step = len(time_step)
	
	##Calculate Success matrix
	success = M2S_item.calc_success(product, num_trial, List_of_Scenarios)
	
	## Calculate running rev
	rev_run = M2S_item.calc_rr(revenue_max,gammaL,duration, product, stage_gate, time_step)
		
	##Calculate open rev  
	rev_open = M2S_item.calc_openrev(revenue_max,gammaL,duration, product, stage_gate, time_step, last_time_step)
	
	##Calculate Discounting Factor
	discounting_factor = M2S_item.calc_discounting_factor(revenue_max,gammaL,trial_cost, product, stage_gate, last_time_step)
	
	
	## Set Probabilities and Outcomes	
	pb = {}
	outcome = {}
	for s in SS:
		pb[s] = List_of_Scenarios[s].probability
		outcome[s] = List_of_Scenarios[s].outcome
			
	resource_max = {}
	for items in model_data._data['max_resource']:
		resource_max[items[0]] = model_data._data['max_resource'][items]
		
	resource_required = {}
	resource_required = model_data._data['resource_requirement']
	
	#######################################################################
	### Generate Non-Anticipativity Constraints
	#######################################################################

	OC = {}
	for s in SS:
		OC[s] = [] 
		for i in prod:
			OC[s].append(List_of_Scenarios[s].outcome[prod.index(i)])

	phi= {}
	phii= {}
	phij ={}

	
	for s in SS:
		for sp in SS:
			if sp > s:
				for i in prod:
					OCtest = list(OC[s])
					OCtest[prod.index(i)] += 1
					OCtest2 = list(OC[s])
					OCtest2[prod.index(i)] += -1
					if OCtest == OC[sp]:
						trl = OC[s][prod.index(i)] + 1
						phi[(s,sp)] = 1
						phii[(s,sp)] = i
						phij[(s,sp)] = trl
					if OCtest2 == OC[sp]:
						trl = OC[sp][prod.index(i)] + 1
						phi[(s,sp)] = 1
						phii[(s,sp)] = i
						phij[(s,sp)] = trl
						
	
	############################################
	### Solve Model
	############################################
	print("Generating Model")
	model = defunction.de(prod,sg,time_step,resource_type,SS,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,pb, success,last_time_step, last_trial, rev_run, rev_open, discounting_factor, phi, phii, phij, outcome)
	print("Solving Model")
	
	sttmr = timer.clock()
	results= opt.solve(model)
	fttmr = timer.clock()
	#fin_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
	
	model.solutions.load_from(results)	
	print("Solve Complete")
	print("Generating Results")
	
	### Make Output Directory
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)					
	
	save_file = "Deterministic_Solution"
	results.write(filename = os.path.join(output_directory, save_file))
						

	Finish_Time = timer.clock()
	Total_Solve_Time = fttmr - sttmr
	Total_Time = Finish_Time - start_time
	Objective_Value = results['Problem'][0]['Lower bound']
	
	### Generate New File Name
	save_file = "Output" 
		
	### Open save file
	f = open(os.path.join(output_directory, save_file),	"w")
		
	### Generate file contents
	algorithm_time = 'Total Solve Time:' + ' ' + str(Total_Solve_Time)
	f.write(algorithm_time + '\n')
		
	algorithm_time = 'Total Time:' + ' ' + str(Total_Time)
	f.write(algorithm_time + '\n')
	
	objective = "ENPV:" + " " + str(Objective_Value)
	f.write(objective + '\n')
	
	#total_resource = "Total Memory:" + " " + str(fin_mem-init_mem)
	#f.write(total_resource + "\n")
	
	f.close()
	
def deterministic_PRDP_solve_with_return(mipgap, model_data, output_directory):
	### Start Solution Timer
	start_time = timer.clock()
	init_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

	##Solver Choice
	opt = SolverFactory("cplex")
	options = Options()
	opt.options.mip_tolerances_mipgap = mipgap
	
	
	##########################################
	### Generate Scenario
	##########################################
	
	#### Problem Info For Scenario Generation
	num_product = len(model_data._data['product'][None])
	prod = model_data._data['product'][None]
	
	num_trial = len(model_data._data['trial'][None])
	sg = model_data._data['trial'][None]
	
	prob = model_data._data['probability']
	num_ts = len(model_data._data['time_step'][None])
	
	### Generate all possible outcomes
	Outcomes = itertools.product(range(num_trial + 1), repeat = num_product)
	Outcomes = tuple(Outcomes)
	
	### From Outcomes Name and Generate Scenarios
	scenario = 1
	List_of_Scenarios = {}
	SS=[]
	
	for items in Outcomes:
		scenario_name = scenario
		List_of_Scenarios[scenario_name] = scenario_class.scenario(items,prob, prod,sg)
		SS.append(scenario_name)
		scenario += 1
	
	##########################################################
	### Input Parameters to Solver
	##########################################################
	
	rev_max = {}
	gammaL = {}
	gammaD = {}
	duration = {}
	trial_cost = {}
	revenue_max = {}
	success = {}
	rev_run = {}
	rev_open = {}
	discounting_factor ={}
	
	##Set product
	product = model_data._data['product'][None]
		
	##Set stage_gate
	stage_gate = model_data._data['trial'][None]
	
	## Set time step
	time_step = model_data._data['time_step'][None]
	
	##Set resource type
	resource_type = model_data._data['resource_type'][None]
	
	## Set duration
	duration = model_data._data['trial_duration']
	
	## Set trial cost
	trial_cost = model_data._data['trial_cost']
	
	## Set Discount Values
	for items in model_data._data['gammaL']:
		gammaL[items[0]] = model_data._data['gammaL'][items]
		
	for items in model_data._data['gammaD']:
		gammaD[items[0]] = model_data._data['gammaD'][items]
	
	## Set Maximum Revenue	
	for items in model_data._data['maximum_revenue']:
		revenue_max[items[0]] = model_data._data['maximum_revenue'][items]
		
	## Set Last Trial
	last_trial = len(stage_gate)
	
	last_time_step = len(time_step)
	
	##Calculate Success matrix
	success = M2S_item.calc_success(product, num_trial, List_of_Scenarios)
	
	## Calculate running rev
	rev_run = M2S_item.calc_rr(revenue_max,gammaL,duration, product, stage_gate, time_step)
		
	##Calculate open rev  
	rev_open = M2S_item.calc_openrev(revenue_max,gammaL,duration, product, stage_gate, time_step, last_time_step)
	
	##Calculate Discounting Factor
	discounting_factor = M2S_item.calc_discounting_factor(revenue_max,gammaL,trial_cost, product, stage_gate, last_time_step)
	
	
	## Set Probabilities and Outcomes	
	pb = {}
	outcome = {}
	for s in SS:
		pb[s] = List_of_Scenarios[s].probability
		outcome[s] = List_of_Scenarios[s].outcome
			
	resource_max = {}
	for items in model_data._data['max_resource']:
		resource_max[items[0]] = model_data._data['max_resource'][items]
		
	resource_required = {}
	resource_required = model_data._data['resource_requirement']
	
	#######################################################################
	### Generate Non-Anticipativity Constraints
	#######################################################################

	OC = {}
	for s in SS:
		OC[s] = [] 
		for i in prod:
			OC[s].append(List_of_Scenarios[s].outcome[prod.index(i)])

	phi= {}
	phii= {}
	phij ={}

		
	for s in SS:
		for sp in SS:
			if sp > s:
				for i in prod:
					OCtest = list(OC[s])
					OCtest[prod.index(i)] += 1
					OCtest2 = list(OC[s])
					OCtest2[prod.index(i)] += -1
					if OCtest == OC[sp]:
						trl = OC[s][prod.index(i)] + 1
						phi[(s,sp)] = 1
						phii[(s,sp)] = i
						phij[(s,sp)] = trl
					if OCtest2 == OC[sp]:
						trl = OC[sp][prod.index(i)] + 1
						phi[(s,sp)] = 1
						phii[(s,sp)] = i
						phij[(s,sp)] = trl
						
	
	############################################
	### Solve Model
	############################################
	model = defunction.de(prod,sg,time_step,resource_type,SS,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,pb, success,last_time_step, last_trial, rev_run, rev_open, discounting_factor, phi, phii, phij, outcome)
	
	sttmr = timer.clock()
	results= opt.solve(model)
	fttmr = timer.clock()
	fin_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
	
	model.solutions.load_from(results)	
	
	Scenario_Results = {}	
	for t in time_step:
		for s in SS:
			for i in product:
				for j in stage_gate:
					if model.Decision_X[i,j,t,s].value == 1:
						index = product.index(i)
						jndex = stage_gate.index(j)
						tndx = time_step.index(t)
						try: 
							Scenario_Results[(i,j,t)]
						except:
							Scenario_Results[(i,j,t)] = 1
		
	### Make Output Directory
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)					
	
	save_file = "Deterministic_Solution"
	results.write(filename = os.path.join(output_directory, save_file))
						

	Finish_Time = timer.clock()
	Total_Solve_Time = fttmr - sttmr
	Total_Time = Finish_Time - start_time
	Objective_Value = results['Problem'][0]['Lower bound']
	
	### Generate New File Name
	save_file = "Output" 
		
	### Open save file
	f = open(os.path.join(output_directory, save_file),	"w")
		
	### Generate file contents
	algorithm_time = 'Total Solve Time:' + ' ' + str(Total_Solve_Time)
	f.write(algorithm_time + '\n')
		
	algorithm_time = 'Total Time:' + ' ' + str(Total_Time)
	f.write(algorithm_time + '\n')
	
	objective = "ENPV:" + " " + str(Objective_Value)
	f.write(objective + '\n')
	
	total_resource = "Total Memory:" + " " + str(fin_mem-init_mem)
	f.write(total_resource + "\n")
	
	f.write(str(Scenario_Results) + "\n")
	
	f.close()
	
	from Core.Solvers.MSSP.MSSP_Results_Object import MSSP_Results_Object
	return_object = MSSP_Results_Object(Objective_Value, Total_Solve_Time,(fin_mem-init_mem), Total_Time)
	 
	return return_object

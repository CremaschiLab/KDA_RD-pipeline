import os
import sys
import pdb

def calc_success(product, num_trial, List_of_Scenarios):
	## Generates a matrix based on the success of each product in each scenario
	success = {}
	try:
		len(List_of_Scenarios)		
		for scenario in List_of_Scenarios:
			oc = 0
			while oc < len(List_of_Scenarios[scenario].outcome):
				coords = (product[oc], scenario)
				if List_of_Scenarios[scenario].outcome[oc] == num_trial:
					success[coords] = 1
				else:
					success[coords] = 0
				oc += 1
	except:
		oc = 0
		while oc < len(List_of_Scenarios.outcome):
			coords = (product[oc])
			if List_of_Scenarios.outcome[oc] == num_trial:
				success[coords] = 1
			else:
				success[coords] = 0
			oc += 1
	

	return success

def calc_rr(revenue_max,gammaL,duration, product, trial, time_step):
	##Calculates the Running Revenue according to the formulation given by Colvin
	rr = {}
	for i in product:
		for j in trial:
			for t in time_step:
				rr[(i,j,t)] = revenue_max[i] - gammaL[i] * ( t + sum(duration[(i,k)] for k in trial if k >= j))
				
	return rr 

def calc_openrev(revenue_max,gammaL,duration, product, stage_gate, time_step, Last_Time_Step):
	##Calculates the Open Revenue according to the formulation given by Colvin
	opnrev = {}
	for i in product:
		for j in stage_gate:
			opnrev[(i,j)] = revenue_max[i] - gammaL[i] * ( Last_Time_Step + sum(duration[(i,k)] for k in stage_gate if k >= j))
				
	return opnrev 

def calc_discounting_factor(revenue_max,gammaL,trial_cost, product, stage_gate, Last_Time_Step):
	##Calculates the discounting factor according to the formulation given by Colvin
	fij = {}
	for i in product:
		for j in stage_gate:
			top = .9 * revenue_max[i] - gammaL[i]* Last_Time_Step - sum(trial_cost[(i,k)] for k in stage_gate if k >= j) 
			bottom = (revenue_max[i] - gammaL[i] * Last_Time_Step)
			fij[(i,j)] = top/bottom
	return fij



import sys
import os
from coopr.opt import SolverFactory, SolverManagerFactory, SolverStatus, TerminationCondition, SolutionStatus
from pyutilib.misc import Options
from defunction import SAA_LP, deLR
import pdb
import gc

def Run_FSNAC(problem_data, fixed_parameters,output_directory):
	opt = SolverFactory("cplex")

	options = Options()
	opt.options.mip_tolerances_mipgap = .0001
	opt.options.mip_tolerances_absmipgap = .0001
	
	####################################################################
	### 	Generate NACs
	####################################################################
	phiij = {}
	OC = {}
	prod = problem_data.product
	SS = problem_data.SS
	pb = {}
	outcome = {}
	
	for s in SS:
		pb[s] = problem_data.List_of_Scenarios[s].probability
		outcome[s] = problem_data.List_of_Scenarios[s].outcome			
	
		
	from Progressive_NAC import Progressive_NAC
	
	phiij = Progressive_NAC(fixed_parameters, problem_data.product, problem_data.stage_gate,problem_data.SS, outcome)
	###phi,phii,phij = Progressive_NAC(fixed_parameters, problem_data.product, problem_data.stage_gate,problem_data.SS, outcome)
							
	####################################################################
	###				Generate Model
	####################################################################
	
	model = SAA_LP(problem_data.product, problem_data.stage_gate, problem_data.time_step, problem_data.resource_type,problem_data.SS,problem_data.resource_max,problem_data.gammaL,problem_data.gammaD,problem_data.duration,problem_data.trial_cost,problem_data.resource_required, problem_data.revenue_max,pb, problem_data.success,problem_data.Last_Time_Step, problem_data.last_trial, problem_data.running_revenue, problem_data.open_revenue, problem_data.discounting_factor, phiij, outcome)
	
	###model = deLR(problem_data.product, problem_data.stage_gate, problem_data.time_step, problem_data.resource_type,problem_data.SS,problem_data.resource_max,problem_data.gammaL,problem_data.gammaD,problem_data.duration,problem_data.trial_cost,problem_data.resource_required, problem_data.revenue_max,pb, problem_data.success,problem_data.Last_Time_Step, problem_data.last_trial, problem_data.running_revenue, problem_data.open_revenue, problem_data.discounting_factor, phi, phii,phiij, outcome)

	####################################################################
	###				Creating Instance
	####################################################################
	instance = model.create()
	
	####################################################################
	### 		Fix Parameters Based on Scenario Outcomes
	####################################################################
	
	list_o_fixes = {}
	for s in SS:
		for itms in fixed_parameters:
			for jtms in fixed_parameters[itms]:
				if len(jtms) == 0:
					instance.Decision_X[itms[0],itms[1],itms[2] + 1,s].value = itms[3]
					instance.Decision_X[itms[0],itms[1],itms[2] + 1,s].fixed = True
					list_o_fixes[(itms[0],itms[1],itms[2] + 1, s)] = itms[3]
				else:
					###pdb.set_trace()
					cntr = 0
					for ktms in jtms:
						if ktms[2] == 0:
							if outcome[s][ktms[0]] == ktms[1]:
								cntr += 1
						else:
							if outcome[s][ktms[0]] > ktms[1]:
								cntr += 1
					if cntr == len(jtms):
						instance.Decision_X[itms[0],itms[1],itms[2] +1,s].value = itms[3]
						instance.Decision_X[itms[0],itms[1],itms[2]+1,s].fixed = True
						list_o_fixes[(itms[0],itms[1],itms[2] + 1, s)] = itms[3]
	
	
	####################################################################
	### 				Preprocess to Fix Decisions
	####################################################################
	del model
	instance.preprocess()
	
	####################################################################
	### 						Solve 
	####################################################################			
	results= opt.solve(instance)
	instance.load(results)	
	
	####################################################################
	### 					Write Output
	####################################################################
	save_file = 'FSNAC Solution Details'
	save_file2 = 'phiij'
	save_file3 = 'model_file'
	
	### Open save file
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)
		
	f = open(os.path.join(output_directory, save_file),	"w")
	
	transformed_results = instance.update_results(results)
	tr = str(transformed_results)
	f.write(tr + '\n')
	f.close()
	
	f = open(os.path.join(output_directory, save_file2),	"w")
	phiij = str(phiij)
	f.write(phiij + '\n')
	f.close()
	
	del instance
	del transformed_results

	if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
		return results.solution.objective['__default_objective__']['Value']
	else:
		pdb.set_trace()

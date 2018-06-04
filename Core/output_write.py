import sys
import os
import pdb

def _write(Evaluated_Solution, Solution, output_directory,solver,data_file):
	
	
	### Generate New File Name
	save_file =  str(solver) + "_" + str(data_file) + "_" + "Output" 
	
	### Open save file
	f = open(os.path.join(output_directory, save_file),	"w")
	
	### Generate file contents
	
	algorithm_time = 'Algorithm Time:' + ' ' + str(Solution.output['algorithm_time'])
	f.write(algorithm_time + '\n')
	
	eval_time = 'ENPV Evaluation Time:' + ' ' + str(Evaluated_Solution.Evaluation_Time)
	f.write(eval_time + '\n')
	
	objective = "ENPV:" + " " + str(Evaluated_Solution.ENPV)
	f.write(objective + '\n')
	
	results = "Results:" + " " + str(Solution.output['results'])
	f.write(results + '\n')
	
	pc = "Problem Count:" + " " + str(Solution.output['problem_count'])
	f.write(pc + '\n')
	
	sp_runtime =  "Subproblem Runtime:" + " " + str(Solution.output['runtime'])
	f.write(sp_runtime + '\n')
	
	sp_realizations = "Subproblem Realizations:" + " " + str(Solution.output['sub_problem_realizations'])
	f.write(sp_realizations + '\n')
		
	### Close File
	f.close()

def _write_EOSS(ENPV, Solution,Total_Time, fixed_parameters, output_directory,solver):
	
	### Generate New File Name
	save_file =  str(solver) + "_" + "Output" 
	
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)
	
	### Open save file
	f = open(os.path.join(output_directory, save_file),	"w")
	
	### Generate file contents
	
	fixed_parms = 'Fixed Parameters:' + ' ' + str(fixed_parameters)
	f.write(fixed_parms + '\n')
	
	algorithm_time = 'Algorithm Time:' + ' ' + str(Total_Time)
	f.write(algorithm_time + '\n')
	
	objective = "ENPV:" + " " + str(ENPV)
	f.write(objective + '\n')
	
	results = "Results:" + " " + str(Solution)
	f.write(results + '\n')
	
		
	### Close File
	f.close()

def _write_Bounding_Procedure(upper_bounds, branch_definition, fixed_parameters, output_directory, Total_Time):
	
	### Generate New File Name
	save_file =  "Bounding Variables" 
	
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)
	
	### Open save file
	f = open(os.path.join(output_directory, save_file),	"w")
	
	### Generate file contents
	
	fixed_parms = 'Fixed Parameters:' + ' ' + str(fixed_parameters)
	f.write(fixed_parms + '\n')
	
	algorithm_time = 'Algorithm Time:' + ' ' + str(Total_Time)
	f.write(algorithm_time + '\n')
	
	algorithm_time = 'Upper Bounds:' + ' ' + str(upper_bounds)
	f.write(algorithm_time + '\n')
	
	objective = "Branch Definition:" + " " + str(branch_definition)
	f.write(objective + '\n')
	
	
		
	### Close File
	f.close()

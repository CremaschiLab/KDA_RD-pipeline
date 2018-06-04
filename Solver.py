import os
import sys
import Core.DataImport.parse_data_cmds 
import Core.DataImport.import_data_class as import_data_class
import time
import pdb


def solve_function(solve_options):
	
	### Define Empty Options Variable
	optcmds = {}

	### Split list of Parsed Commands on equal signs
	for i in solve_options[1:]:
		try:
			cmd = i.split('=',1)
			optcmds[cmd[0]] = cmd[1]
		except:
			try:
				optcmds['none'].append(i)
			except:
				optcmds['none'] = [i]

	### Lists of acceptable inputs	
	list_of_solvers = ['kda','mtssp','mssp','saa','eoss']
	_cmds = ['linear-relaxation','min_step','max_step','all_time']
	solver_options = ['min_solve','max_solve', 'probabilistic', 'penalty', 'SAA', 'PH', 'deterministic_initializations']
	MSSP_opts = []
	_opts = []

	### Sort the options chosen
	for i in optcmds:
		cmd = i.lower()
		if cmd == 'solve-method':
			if optcmds[i].lower() in list_of_solvers:
				solver_cmd = optcmds[i].lower()
		elif cmd == 'data-file':
		
			problem_file_directory = os.path.dirname(os.path.realpath(__file__)) + '/Problem Files/'
		
			### If the file is in the problem files folder then the filename is the sub-directory plus the filename
			if os.path.isfile(os.path.join(problem_file_directory, optcmds[i])):
				import_file_name = os.path.join(problem_file_directory,optcmds[i])
			
			### Otherwise assume the file is in the current directory
			else:	
				import_file_name = optcmds[i]
			
			### file name for output directory	
			file_name = optcmds[i]
			
		elif cmd == 'solver':
			solver = optcmds[i].lower()
		elif cmd == 'mipgap':
			try:
				mipgap = float(optcmds[i])
			except:
				raise Exception("MIP Gap must be a number")
		elif cmd == 'none':
			for ntms in optcmds[cmd]:
				if ntms.lower() in solver_options:
					_opts.append(ntms)
			
		
		else:
			raise Exception("Option " + str(i) + " Not Supported")
			exit()


	### Problem Data
	try:
		file_reader = ['import', import_file_name]
	except:
		raise Exception("Must Specify File")

	
	### Set defaults
	try: 
		solver
	except:
		solver = 'cplex'

	try:
		mipgap
	except:
		mipgap = .001

	### Set output directory
	current_directory = os.path.dirname(os.path.realpath(__file__))
	current_date = time.strftime('%m_%d_%Y', time.gmtime())

	if len(_opts) == 0:
		output_directory = current_directory + '/Solutions/' + str(file_name) + '/' + str(solver_cmd) + '_' + current_date + '/'
	else:
		output_directory = current_directory + '/Solutions/' + str(file_name) + '/' + str(solver_cmd) + '_' + current_date + '_'+ str(_opts) + '/'
	
	### Import Data
	print("Importing data from " + str(file_name))    
	model_data = import_data_class.Data_Collection(file_reader)

	### Import Solver method based on solver type and generate solve class
	if solver_cmd == 'kda':
		import Core.Solvers.KDA.KDA_Solution_Class as Solve
	
		### Check options for KDA
		kda_mipgap = .001
		Solution = Solve.KDA(model_data, solver, kda_mipgap, output_directory,_opts)
	
		### Import Solution Evaluation
		import Core.Solvers.KDA.Evaluate_KDA_PRDP as Evaluate_KDA
		
		### Calculate Equivalent ENPV
		results = Solution.output['results']
		sp_realizations = Solution.output['sub_problem_realizations']
		Evaluated_Solution = Evaluate_KDA.KDA_PRDP_results(model_data,results,sp_realizations, output_directory)
	
	
		### Write results to Consolidated file
		import Core.output_write as output_write
		output_write._write(Evaluated_Solution,Solution,output_directory,solver_cmd, file_name)
		
	
		### If option exists, solve using initializations
		if 'deterministic_initializations' in _opts:
			
			### Send Results to Deterministic model
			from Core.Solvers.KDA.KDA_Deterministic_Initializations import det_inits 
			print("Starting Deterministic Solve")
			model_type = model_data._data['model_type'][None][0]
			warmstart_output_directory = output_directory + '/Warmstart/'
			det_inits(Solution, model_type, model_data, warmstart_output_directory, mipgap)
			
	
	elif solver_cmd == 'mtssp':
		import Core.Solvers.MTSSP.MTSSP_Solution_Class as Solve
	
		### Check MTSSP Options
		Solution = Solve.MTSSP(model_data,solver,mipgap,output_directory, _opts)
	
		### Import Solution Evaluation
		import Core.Evaluate_MTSSP as Evaluate_MTSSP
	
	elif solver_cmd == 'mssp':
		### Check for MSSP options
		if len(_opts) == 0:
			from Core.Solvers.MSSP.Deterministic_Solver import Deterministic_PRDP_Solve as Solve
			Solution = Solve(mipgap,model_data, output_directory)
		
	elif solver_cmd == 'saa' :
		import Core.Solvers.SAA.SAA_Solution_Class as Solve
		Solution = SAA(model_data)

	elif solver_cmd == 'eoss' :
		import Core.Solvers.EOSS.EOSS_Solution_Class as Solve
		
		### Solve EOSS problem
		Solution = Solve.EOSS(model_data)

	return 

if __name__ == "__main__":
	### Parse Commands
	solve_options = sys.argv
	solve_function(solve_options)

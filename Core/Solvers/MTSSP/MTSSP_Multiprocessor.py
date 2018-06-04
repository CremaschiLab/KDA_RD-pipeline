import sys
import os
import pdb
import multiprocessing as mp

def realization_MP(list_to_process, model_type, parameter, ts, results):
	
	### Get core count for number of processes
	process_count = mp.cpu_count()
	
	### Generate Pool
	mp.Pool(processes = process_count)
	
	### Run model type realizations
	
	####################################################
	### Model Specific Realizations Routing Block
	####################################################
	if model_type == 'PDRP':
		from PRDP_Data_Processing import PRDP_Realizations as function_name
		arg_input = [ts,parameter, results]
	
	results = [pool.apply(function_name, args = tuple([s] + arg_input)) for s in list_to_process]
	
		
	Scenario_Sets = []
	
	for items in results:
		Scenario_Sets += items
	
	return Scenario_Sets
	

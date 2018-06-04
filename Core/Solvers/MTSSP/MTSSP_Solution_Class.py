import sys
import os
from coopr.opt import SolverFactory, SolverManagerFactory
import itertools
from pyutilib.misc import Options
import MTSSP_Item
import MTSSP_Multiprocessor
import time as timer
import pdb
import gc
import re

class MTSSP:
	def __init__(self, model_data, solver, mipgap, solve_output, _opts):
		self.mipgap = mipgap
		self.solver = solver
		self._opts = _opts
		
		### Calculate MTSSP parameters
		mtssp_data = MTSSP_Item.MTSSP_Data_Processing(model_data)
		
		### Implement MTSSP Algorithm
		solution = self.mtssp_solver(mtssp_data,solve_output,_opts)
		
	
	def mtssp_solver(self, mtssp_data, solve_output, _opts):
		### Start Timer
		start_time = timer.clock()
		problem_counter = 0
		
		### Set output directory
		output_directory = solve_output
		
		pdb.set_trace()
		### Set planning horizon length
		Last_Time_Step = mtssp_data.Parameters.Last_Time_Step
		
		### Set iterand as 0
		ts = 0
		
		### Set Empty Parameters
		Scenario_Sets = {}
			
		###############################################################
		### Generate Results Matrix ( Model Specific)
		###############################################################
		if mtssp_data.model_type == 'PDRP':
			results = PRDP_Data_Processing.results_matrix_generator(mtssp_data.Parameters)
				
		### Solve Loop
		while ts < Last_Time_Step:
			
			
			### Check if loop is at the beginning
			if ts != 0:
				
				### Check for Realizations
				Scenario_Sets[ts] = MTSSP_Multiprocessor.realization_MP(Scenario_Sets[ts-1], mtssp_data.model_type, mtssp_data.Parameters, ts, results)
			
					
					
				
				### Determine Whether to Solve and Solve
				
				for scenarios in Scenario_Sets[ts]:	
					
					####################################################
					### Model Specific Resource Utilization Routing Block
					####################################################
					if mtssp_data.model_type == 'PDRP':
						resource_count[ts] = PRDP_Data_Processing.resource_utilization(mtssp_data.Parameters, results)	
					
		return True
		

import sys
import os
from pyomo.environ import *
from pyomo.opt import SolverFactory
import itertools
from pyutilib.misc import Options
import time as timer
import pdb
import gc
import re

class KDA:
	def __init__(self, model_data, solver, mipgap,solve_output, _opts, fixed_parameters={}, penval = 0):
		self.mipgap = mipgap
		self.solver = solver
		self._opts = _opts
		self.fixed_parameters = fixed_parameters
		self.model_type = model_data._data['model_type'][None][0]
		
		### Process knapsack data
		if self.model_type == 'PRDP':
			from Core.Solvers.KDA import knapsack_item
			knapsack_data = knapsack_item.knapsack_data_processing(model_data)
			
		
		### Solve knapsack
		solution = self.kda_solver(knapsack_data,model_data,solver,mipgap,solve_output, _opts, penval)
		
		self.output = solution
			
	def kda_solver(self, knapsack_data,model_data, solver, mipgap, solve_output, _opts, penval):
		## Start Solution Timer
		start_time = timer.clock()
		problem_count = 0
				
		output_directory = solve_output
		
		## Set the number of time steps total
		ts = len(model_data._data['time_step'][None])
		
		### declare time
		time = 0
		sp_solve= {}
		ex = {}
			
		#### Loop over all steps
		while time < ts:
				
			##Set the parameters that are time specific
			if time == 0:
					
				### Initialize Time Dependent Parameters
				### Class wide parameters
				self.run_time = {}
				self.temp_dict = {}
				self.temp_item_selection = {}
				self.fixed_items = {}
					
				### Method wide Parameters
				results_storage = {}
				item_monitor = {}
				sp_realizations = {}
					
				### Declare Sub-Problem Name
				sub_problem = '0'
				
				###Declare Max Duration
				max_duration = 0
					
				########################################################
				###		Create Existance Vector (Model Specific)
				########################################################
				existance = {}
				if self.model_type == 'PRDP':
					from Core.Solvers.KDA.KDA_PRDP_Functions import initial_existance
					existance[('0',0)] = initial_existance(knapsack_data)
					
				########################################################
				### Determine Fixed Parameters (Model Specific)
				########################################################
				if len(self.fixed_parameters) != 0:		
					if self.model_type == 'PRDP':
						from Core.Solvers.KDA.KDA_PRDP_Functions import initial_fixed_parameters
						self.fixed_items[sub_problem] = initial_fixed_parameters(self.fixed_parameters,knapsack_data, model_data)
				else:
					self.fixed_items[sub_problem] = []
						
				### Increment problem counter
				problem_count += 1	
					
				########################################################
				###     Solve t=0 Problem Based on Solve Options
				########################################################
				if 'min_solve' in _opts:
					##Solve using min_solve_solver
					self.min_solve_solver(knapsack_data, item_monitor, model_data,existance,output_directory,sub_problem,time,max_duration,penval)
				elif 'max_solve' in _opts:
					### Solve using max_solve_solver
					self.max_solve_solver(knapsack_data, model_data,existance,output_directory,sub_problem,time,max_duration,penval)
				else:
					### Solve using min_solve_solver
					self.min_solve_solver(knapsack_data, item_monitor, model_data,existance,output_directory,sub_problem,time,max_duration,penval)
				
				### Store Solution
				results_storage[time] = dict(self.temp_item_selection)
				item_monitor[time] = dict(self.temp_dict)
				
				
				### Increment time	
				time += 1
			else:
				
				########################################################
				### 		Determine Sub-Problem Generation
				########################################################
				item_monitor[time] = {}	
				for i in item_monitor[time-1]: ### THIS IS WHERE PARALLELIZATION SHOULD OCCUR
					finished_items = []
					generate_subproblems = False
					
					### Based on _opts determine whetherto generate sub-problems
					if 'min_solve' in _opts:
						################################################
						### Determine Sub-Problems (Model Specific)
						################################################
						if self.model_type == 'PRDP':
							from Core.Solvers.KDA.KDA_PRDP_Functions import min_solve_sp_generation
							generate_subproblems, finished_items = min_solve_sp_generation(item_monitor,time,i)
					
					elif 'max_solve' in _opts:
						################################################
						### Determine Sub-Problems (Model Specific)
						################################################ 
						if self.model_type == 'PRDP':
							from Core.Solvers.KDA.KDA_PRDP_Functions import max_solve_sp_generation
							generate_subproblems, finished_items = max_solve_sp_generation(item_monitor,time,i)	
							
					else:
						################################################
						### Determine Sub-Problems (Model Specific)
						################################################ 
						if self.model_type == 'PRDP':
							from Core.Solvers.KDA.KDA_PRDP_Functions import every_solve_sp_generation
							generate_subproblems,finished_items = every_solve_sp_generation(item_monitor,time,i)
					
					####################################################
					### 		Generate Sub-Problems
					####################################################
					if generate_subproblems == True:
						if len(finished_items) > 0:
						
						################################################
						###    Model Specific Sub-Problem Generation
						################################################	
							if self.model_type == 'PRDP':
								from Core.Solvers.KDA.KDA_PRDP_Functions import PRDP_SubProblem_Generation
								sp_realizations, sp_solve, item_monitor = PRDP_SubProblem_Generation(finished_items, i, time, item_monitor,sp_solve,sp_realizations)
							
					else:
						item_monitor[time][i] = item_monitor[time-1][i]
				
				########################################################
				###  		Calculate Existance Vectors Items
				########################################################
				for i in item_monitor[time]:  ### THIS IS ANOTHER PLACE FOR PARALLELIZATION
					####################################################
					### Model Specific Existance Vector Determiniation
					####################################################
					if self.model_type == 'PRDP':
						from Core.Solvers.KDA.KDA_PRDP_Functions import non_initial_existance_vector
						existance = non_initial_existance_vector(i, time, model_data, existance, knapsack_data, item_monitor, _opts, sp_realizations, results_storage)
						
				
				
				########################################################
				###  	Update Parameters and Solve Sub-Problems
				########################################################
				for i in item_monitor[time]:  ### THIS IS ANOTHER PLACE FOR PARALLELIZATION	
					####################################################
					###  	Determine if Solving is Needed 
					####################################################
					if self.model_type == 'PRDP':
						from Core.Solvers.KDA.KDA_PRDP_Functions import do_solve_calc
						do_solve = do_solve_calc(i, time, existance)
					
					if do_solve == 0:
						try:
							results_storage[time]
						except:
							results_storage[time] = {}
							
						results_storage[time][i] = ()
					
					else:
						################################################
						### Determine Sub-Problem Fixed Parameters (Model Specific)
						################################################
						if len(self.fixed_parameters) > 0:	
							if self.model_type == 'PRDP':
								from Core.Solvers.KDA.KDA_PRDP_Functions import fixed_item_generator
								self.fixed_items[i] = fixed_item_generator(i,time,sp_realizations, knapsack_data, model_data, self.fixed_parameters)
						else:
							self.fixed_items[i] = []
						
						################################################
						### 			Minimum Solve 
						################################################
						if 'min_solve' in _opts:
							##Solve using min_solve_solver
							try:
								if time == sp_solve[i]:
				
									max_duration = 0
									
									self.min_solve_solver(knapsack_data, item_monitor[time][i],model_data,existance,output_directory,i,time,max_duration,penval)
									
									### Increment problem counter
									problem_count += 1
									
									## Create dictionary entry for temporary variable with the time key	
									try:
										results_storage[time]
									except:
										results_storage[time] = {}
									results_storage[time][i] = self.Item_Selection
									item_monitor[time][i] += self.temp
								
								else:
									try:
										results_storage[time]
									except:
										results_storage[time] = {}
								
									results_storage[time][i] = ()
							except:
								try:
									results_storage[time]
								except:
									results_storage[time] = {}
							
								results_storage[time][i] = ()
						
					
								
						
						
						################################################
						### 			Maximum Solve 
						################################################						
						elif 'max_solve' in _opts:
							### If there are no active items solve the knapsack using data
							
							if item_monitor[time][i] == ():
								
								### Solve using max_solve_solver
								self.max_solve_solver(knapsack_data,model_data,existance,output_directory,i,time,max_duration,penval)
								
								### Increment problem counter
								problem_count += 1
							
								try:
									results_storage[time]
								except:
									results_storage[time] = {}
													
					
								results_storage[time][i] = self.Item_Selection
								item_monitor[time][i] += self.temp
							else:
								try:
									results_storage[time]
								except:
									results_storage[time] = {}
								
								results_storage[time][i] = ()
						################################################
						### 			Everytime Solve 
						################################################				
						else:
							### Solve using min_solve_solver
							
							self.min_solve_solver(knapsack_data, item_monitor[time][i],model_data,existance,output_directory,i,time,max_duration,penval)	
							
							### Increment problem counter
							problem_count += 1
							
							## Create dictionary entry for temporary variable with the time key	
							try:
								results_storage[time]
							except:
								results_storage[time] = {}
													
					
							results_storage[time][i] = self.Item_Selection
							item_monitor[time][i] += self.temp
							
				## Increment Time
				
				time += 1
				
		finish_time = timer.clock()
		total_time = finish_time - start_time	
		answers = self.results_format(sp_realizations, problem_count, results_storage, total_time)
		
		return answers					
	
	def max_solve_solver(self, knapsack_data, model_data, existance, output_directory, sub_problem,time, max_duration,penval):
			
		##Solver info
		opt = SolverFactory(self.solver)
		options = Options()
		opt.options.mip_tolerances_mipgap = self.mipgap
		
		################################################################
		### 			Generate Model (Model Specific)
		################################################################
		if self.model_type == 'PRDP':
			### Define Item List
			items = knapsack_data.ItemList
			
			### Generate Model
			from Core.Solvers.KDA.KDA_PRDP_Functions import PRDP_Max_Solve_Model_Generator
			model = PRDP_Max_Solve_Model_Generator(knapsack_data, model_data, existance, sub_problem, time, max_duration, self._opts, penval)
		
		### Initiate Timer
		st = timer.clock()
		
		################################################################
		### 					Create Instance
		################################################################
		
		for items in self.fixed_items[sub_problem]:
			model.x[items[0]] = items[1]
			model.x[items[0]].fixed = True
		
		model.preprocess()
		
		################################################################			
		###						 Solve Model
		################################################################
		results = opt.solve(model)
		
		### Take finish Time
		ft = timer.clock()
		
		################################################################
		### 					Process Results
		################################################################		
		### Make Output Directory
		if 'quiet' not in self._opts:
			if not os.path.exists(output_directory):
				os.makedirs(output_directory)
		
		## Load Results
		model.solutions.load_from(results)
					
		#### Save problem information
		if 'quiet' not in self._opts:
			save_file = "IntKs_" + str(sub_problem) + "_" + str(time) + ".json"
			results.write(filename = os.path.join(output_directory, save_file))
		
		
		
		### Create Performance variables for problem runtime and item management
		self.temp = ()
		self.Item_Selection = ()
		
		## Store the items packed in the knapsack in temporary variable
		for i in items:
			if model.x[i].value == 1:
				
				########################################################
				### 		Store Results (Model Specific)
				########################################################
				if self.model_type == 'PRDP':
					from Core.Solvers.KDA.KDA_PRDP_Functions import results_processing
					obj1, obj2 = results_processing(knapsack_data, model_data,i, time)				
					
				### Items Selected
				self.Item_Selection += (obj1,)
								
				### Append item
				self.temp += (obj2,)

		if time == 0:
			self.temp_dict[sub_problem] = self.temp	
			self.temp_item_selection[sub_problem] = self.Item_Selection
		
		## Store solve time
		self.run_time[(sub_problem,time)] = ft - st		

	def min_solve_solver(self, knapsack_data, active_item_list, model_data,existance,output_directory,sub_problem,time,max_duration,penval):
		
		##Solver info
		opt = SolverFactory(self.solver)
		options = Options()
		opt.options.mip_tolerances_mipgap = self.mipgap
		
		################################################################
		### 			Generate Model (Model Specific)
		################################################################
		if self.model_type == 'PRDP':
			### Define Item List
			items = knapsack_data.ItemList
			
			### Generate Model
			if 'greedy' in self._opts:
				from Core.Solvers.KDA.KDA_PRDP_Functions import PRDP_Min_Solve_Model_Generator_Greedy
				model = PRDP_Min_Solve_Model_Generator_Greedy(knapsack_data, model_data, active_item_list, existance, sub_problem, time, max_duration, self._opts, penval)
			else:
				from Core.Solvers.KDA.KDA_PRDP_Functions import PRDP_Min_Solve_Model_Generator
				model = PRDP_Min_Solve_Model_Generator(knapsack_data, model_data, active_item_list, existance, sub_problem, time, max_duration, self._opts, penval)
		
		### Initiate Timer
		st = timer.clock()
		
		################################################################
		### 					Create Instance
		################################################################
		
	
		for (i,j) in self.fixed_items[sub_problem]:
			model.x[i].value = j
			model.x[i].fixed = True
		
		model.preprocess()	
		
		################################################################			
		###						 Solve Model
		################################################################
		results = opt.solve(model)
		
		### Take finish Time
		ft = timer.clock()
		
		################################################################
		### 					Process Results
		################################################################		
		### Make Output Directory
		if 'quiet' not in self._opts:
			if not os.path.exists(output_directory):
				os.makedirs(output_directory)
		
		### Load Results
		model.solutions.load_from(results)
					
		#### Save problem information
		if 'quiet' not in self._opts:
			save_file = "IntKs_" + str(sub_problem) + "_" + str(time) + ".json"	
			results.write(filename = os.path.join(output_directory, save_file))
			
		### Create Performance variables for problem runtime and item management
		self.temp = ()
		self.Item_Selection = ()
		
		## Store the items packed in the knapsack in temporary variable
		for i in items:
			if model.x[i].value == 1:
				
				########################################################
				### 		Store Results (Model Specific)
				########################################################
				if self.model_type == 'PRDP':
					from Core.Solvers.KDA.KDA_PRDP_Functions import results_processing
					obj1, obj2 = results_processing(knapsack_data, model_data,i,time)				
					
				### Items Selected
				self.Item_Selection += (obj1,)
								
				### Append item
				self.temp += (obj2,)

		if time == 0:
			self.temp_dict[sub_problem] = self.temp	
			self.temp_item_selection[sub_problem] = self.Item_Selection
		
		## Store solve time
		self.run_time[(sub_problem,time)] = ft - st			

	def results_format(self, sp_realizations, problem_count, results_storage, total_time):
		answer = {}
		
		answer['sub_problem_realizations'] = sp_realizations
		answer['problem_count'] = problem_count
		answer['results'] = results_storage
		answer['runtime'] = self.run_time
		answer['algorithm_time'] = total_time
		
		return answer					

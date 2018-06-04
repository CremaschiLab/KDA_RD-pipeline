import sys
import os
import itertools
import copy
import math
import multiprocessing as mp
import Core.Solvers.MTSSP.M2S_item as M2S_item
from pyomo.environ import *
from pyomo.opt import SolverFactory
import Core.scenario_class as SC
from Core.Solvers.MSSP import defunction as MSSP

class Decision_Tree:
	def __init__(self, model_data,decs =[],  ub = 0, old_tree = {}):
		""" decs is a list of the decisions you can make and how long it takes to realize the outcome after making the decision
			(i,j,t,tau)
		"""
		if old_tree == {}:
			### Initialize Structures
			self.Branch_Count = 0
			self.Branches = {}
			self.Branch_Def = {}
			self.Branch_Map = {}
			self.Decisions = {}
			
			### Create Branch Box
			t = 0
			planning_horizon = len(model_data._data['time_step'][None])
			while t < planning_horizon:
				self.Branches[t] = []
				t += 1
			
			### Add zero branch
			self.Branches[0] = [0]
			self.Decisions[0]={}
			
			
			### Define 0 realizations for initial branch
			self.Branch_Def[0] = []
			self.Upper_Bound = float('nan')
			self.Branch_Map[0] = [0]
			
			
		else:
			self.Branch_Count = copy.deepcopy(old_tree.Branch_Count)
			self.Branches = copy.deepcopy(old_tree.Branches)
			self.Branch_Def = copy.deepcopy(old_tree.Branch_Def)
			self.Decisions = copy.deepcopy(old_tree.Decisions)
			self.Upper_Bound = copy.deepcopy(old_tree.Upper_Bound)
			self.Branch_Map = copy.deepcopy(old_tree.Branch_Map)
			
	
	def __repr__(self):
		return str(self.Upper_Bound)

	def add_decision(self, model_data, decision, parallel,realization = []):
		""" model_data   -- a dictionary of relevant model information
			decision 	 -- list of (i,j,t,tau,decision(0,1)) decisions for the given realizations 
			realization  -- list of realizations for the branch of the added decisions given as (i,j,realization) 
		"""
		### Determine the time of the added decisions
		time = decision[0][2]
		
		### Convert realization to useable format
		rlzn = realization
				
		### Update Branches
		self._branch_update(time,decision,realization)	
		
					
		### Determine which branch match the realizations
		for b in self.Branch_Def:
							
			if set(self.Branch_Def[b]) == set(rlzn):
				
				### If the branch is found, add decisions to the branch
				try:
					if set(decision) in set(self.Decisions[b][time]):
						print('Error Decisions already Fixed')
					else:
						self.Decisions[b][time] += decision	
					
				except:
					self.Decisions[b][time] = list(decision)
					
					
					
			
		self._Update_UB_FSNAC(time,model_data,parallel)
		
		return
	
	def _branch_update(self,time,decisions,realization):
		self.Branches[time] =[]
		end_branches= []
			
		### Determine the end branches
		for b in self.Decisions:
			pb = 0
			for bs in self.Decisions:
				if b != bs:
					bb = 0
					while bb < len(self.Branch_Map[bs]):
						if self.Branch_Map[bs][bb] == b:
							pb += 1
						bb += 1
			if pb == 0:
				end_branches.append(b)
		
		
		### In each of the end branches determine if there are any realizations
		for b in end_branches:
			
			realized_trials = []
			realized_decs = []
			match_cnt = 0
			does_not_match = False
			
			### Check to see that all the realized trials were started
			for (i,j,realz) in realization:
				
				for t in self.Decisions[b]:
					for (ist,jst,tm,tau,dec) in self.Decisions[b][t]:
						if ist==i and jst==j and tm + tau <= time and dec == 1:
							if (i,j,realz) in self.Branch_Def[b]:
								match_cnt += 1
							elif (i,j,1-realz) in self.Branch_Def[b]:
								does_not_match = True
							else:
								realized_decs.append((ist,jst,tm,tau,dec))
						elif ist==i and jst==j and tm + tau > time and dec == 1:
							does_not_match = True
						
			for t in self.Decisions[b]:
				for (i,j,tm,tau,dec) in self.Decisions[b][t]:
					if tm + tau <= time and dec == 1:
						if (i,j,0) in self.Branch_Def[b] or (i,j,1) in self.Branch_Def[b]:
							pass
						elif (i,j,tm,tau,dec) in realized_decs:
							pass
						else:
							realized_trials.append((ist,jst,tm,tau,dec))
								
			if does_not_match != True:
				if match_cnt + len(realized_decs) == len(realization):
					realized_decs += realized_trials
					if len(realized_decs) > 0:
						self._Create_Branch(b,realized_decs,time)
						end_branches.remove(b)   	
					
		self.Branches[time] += end_branches			
		
		return			
							
		
				
			
	def _Create_Branch(self, parent_branch, decision,time):
		
		### Generate outcomes for each of the new branches
		new_branch_realizations = itertools.product(range(2), repeat = len(decision))
		new_branch_realizations = tuple(new_branch_realizations)
		
		for nbr in new_branch_realizations:
			
			# Increment the branch count
			self.Branch_Count += 1
			
			# The new count represents the branch number
			branch_num = self.Branch_Count
		
			# add the new branch to the list
			self.Branches[time].append(branch_num)
			
			# add the realizations to the branch definition
			self.Branch_Def[branch_num] = copy.deepcopy(self.Branch_Def[parent_branch]) + [decision[i][0:2] + (nbr[i],) for i in range(len(nbr))]
			
			# Add the Branch to the Branch Map
			self.Branch_Map[branch_num] = copy.deepcopy(self.Branch_Map[parent_branch]) + [branch_num]	
			
			self.Decisions[branch_num] = copy.deepcopy(self.Decisions[parent_branch])
			
			
		return
					
			
	def _Update_UB_FSNAC(self,time,model_data,parallel):
		
				
		### Define Constants
		rho = 20
		prod = model_data._data['product'][None]
		trial = len(model_data._data['trial'][None])
		
				
		### Declare empty variable
		w0 = {}
		x_bar = {}
		branch_probability_total = {}
		x = {}
		w = []
		x_non_zero =[]
		non_zeros = []
		cds = {}
		btime = {}
				
		### Determine needed non-anticipativity constraints
		for b in self.Branches[time]:
			
			### Build Variables (these need to be a different shape)
			x[b] = [0]* len(prod)
			
			### Loop over all the decisions and replace last trial completed
			btime_cnt = 0
			for dtime in self.Decisions[b]:
				if btime_cnt < dtime:
					btime_cnt = dtime
					
				for (i,j,tm,tau,dec) in self.Decisions[b][dtime]:
					if dec == 1:
						if x[b][prod.index(i)] <= j:
							x[b][prod.index(i)] = j
			
			btime[b] = btime_cnt		
			### Change Completed trial to the next trial
			i = 0
			while i < len(x[b]):
				if x[b][i] == 0:
					x[b][i] = 1
				elif x[b][i] + 1 > model_data._data['trial'][None][-1]:
					x[b][i] = model_data._data['trial'][None][-1]
				else:
					x[b][i] += 1
					
				i += 1
		
		
		### Determine the size and shape of x_bar, w0, and cds for each branch
		for b in self.Branches[time]:
			
			### Define the latest time that the branches will be differentiated
			tend = len(model_data._data['time_step'][None])
			
			### Determine the soonest time that the branches will differentiated based on the decisions already made
			for t in self.Decisions[b]:
				for (i,j,tm,tau,dec) in self.Decisions[b][t]:
					if dec == 1:
						## If you start a trial find out when it will be realized
						if tm + tau > btime[b]:
							if tm + tau + 1 < tend:
								tend = tm + tau + 1
								
							
			#### Determine the if a constrained trial is started at the next time when is the soonest that the differentiation may occur
			lcd = 0
			while lcd < len(x[b]):
				i = prod[lcd]
				j = x[b][lcd]
				if j <= model_data._data['trial'][None][-1]:
					trial_dur = model_data._data['trial_duration'][(i,j)]
					if btime[b] + 1 + trial_dur < tend:
						tend = btime[b] +  trial_dur + 1
				lcd += 1
						
					
			### Now that we know tend, we need to create appropriate sized variables w0, x_bar, and cds
			var_size = [0 for _ in range((tend - 1))]
			x_bar[b] = [copy.deepcopy(var_size) for _ in range(len(prod))]
			w0[b] = [copy.deepcopy(var_size) for _ in range(len(prod))]
			cds[b] = []
			
			
			t = 0
			while t + 1 < tend:
				k = 0
				while k < len(prod):
					i = prod[k]
					j = x[b][k]
					if j <= model_data._data['trial'][None][-1]:
						if t in self.Decisions[b]:
							if (i,j,t+1,model_data._data['trial_duration'][(i,j)],0) in self.Decisions[b][t] or (i,j,t+1,model_data._data['trial_duration'][(i,j)],1) in self.Decisions[b][t]:
								pass
							else:
								cds[b].append((i,j,t+1))
						else:
							cds[b].append((i,j,t+1))
					k += 1
				t += 1
					
		x_bar_z = copy.deepcopy(x_bar)
		 
					
		### Determine branch probability
		for b in self.Branches[time]:
			p = 1
			for i in self.Branch_Def[b]:
				if i[2] == 0:
					#fail
					p *= (1-model_data._data['probability'][(i[0],i[1])])
				else:
					p *= (model_data._data['probability'][(i[0],i[1])])
			branch_probability_total[b] = p
		
		#### Generate scenario iterable
		Outcomes = itertools.product(range(trial + 1), repeat = len(prod))
			
			
		
		################################################################			
		### First Set of Decisions
		################################################################
		
		### Set MP options
		process_count = 18 * parallel
		np = int(math.ceil(Outcomes.__sizeof__() / (3*parallel)))
		n_sets = 3*parallel
		setlist = self._grouper(Outcomes,np)
		
		### Create Pool
		pool = mp.Pool(n_sets)
		
		### Run Pool
		results = [pool.apply_async(self._first_PH_mpfunc, args=(model_data,tuple(outcome),btime,x_bar_z,cds,branch_probability_total,time)) for outcome in setlist]
		pool.close()
		pool.join()
		
		### Combine Results
		for xcnt in results:
			x_non_zero += xcnt._value[0]
			for b in self.Branches[time]:
				for (i,j,t) in cds[b]:
					x_bar[b][prod.index(i)][t-1] += xcnt._value[1][b][prod.index(i)][t-1]
		
		
		################################################################
		### Second Decision Set
		################################################################
		itr = 0
		tol = .01
		max_iterations = 500
		alpha = 100
		
		while alpha > tol and itr < max_iterations:
			new_x_non_zero = []
			x_bar_new = copy.deepcopy(x_bar_z)
			ENPV = 0
			
			
			############################################################
			###      Results of Iteration
			############################################################
			
			#### Generate scenario iterable
			Outcomes = itertools.product(range(trial + 1), repeat = len(prod))
			
			### Set MP options
			setlist = self._grouper(Outcomes,np)
		
			### Create Pool
			pool = mp.Pool(n_sets)
		
			### Run Pool
			results = [pool.apply_async(self._second_PH_mpfunc, args=(model_data,tuple(outcome),btime,x_bar_z,cds,branch_probability_total,x_bar,x_non_zero,time,rho)) for outcome in setlist]
			pool.close()
			pool.join()
			
			### Consolodate Results
			for xcnt in results:
				new_x_non_zero += xcnt._value[0]
				for b in self.Branches[time]:
					for (i,j,t) in cds[b]:
						x_bar_new[b][prod.index(i)][t-1] += xcnt._value[1][b][prod.index(i)][t-1]
				ENPV += xcnt._value[2]		
			
			### Address NAC between branches
			for t in self.Branches:
				if t < time:
					
					### If there is a difference in branches at a time period
					if set(self.Branches[t]) != set(self.Branches[time]):
						
						### For each of the old branches
						for b_old in self.Branches[t]:
							bfam = []
							
							### Determine if the branches at the current time are children
							for b in self.Branches[time]:
								if b_old in set(self.Branch_Map[b]):
									bfam.append(b)
							
							## Determine the constrained decisions at the time period for the old branch
							xold = [0] * len(prod)
							
							### Loop over all the decisions and replace last trial completed
							for dtime in self.Decisions[b_old]:			
								for d in self.Decisions[b_old][dtime]:
									if d[4] == 1 and dtime:
										if xold[prod.index(d[0])] <= d[1]:
											xold[prod.index(d[0])] = d[1]
				
							### Change Completed trial to the next trial
							i = 0
							while i < len(x[b]):
								if xold[i] == 0:
									xold[i] = 1
								elif xold[i] + 1 > model_data._data['trial'][None][-1]:
									xold[i] = model_data._data['trial'][None][-1]	
								else:
									xold[i] += 1
								i += 1
							
							### Update Xbar new to reflect the family
							cd_old = list(enumerate(xold))
							x_bar_hold = {}
							for (idx,j) in cd_old:
								for brel in bfam:
									if (prod[idx],j,t + 1) in set(cds[brel]):
										try:
											x_bar_hold[(idx,j)] += branch_probability_total[brel] * x_bar_new[brel][idx][t]
										except:
											x_bar_hold[(idx,j)] = branch_probability_total[brel] * x_bar_new[brel][idx][t]
									
							for (idx,j) in cd_old:
								for brel in bfam:
									if (prod[idx],j,t + 1) in set(cds[brel]):
										x_bar_new[brel][idx][t] = x_bar_hold[(idx,j)]
										
							
			############################################################
			### 					Calculate Gk
			############################################################
			gk = 0
			
			#### Generate scenario iterable
			Outcomes = itertools.product(range(trial + 1), repeat = len(prod))
			
			### Set MP options
			np_high = int(math.ceil(Outcomes.__sizeof__() /process_count))
			setlist = self._grouper(Outcomes,np_high)
		
			### Create Pool
			pool = mp.Pool(process_count)
		
			### Run Pool
			results = [pool.apply_async(self._mp_gk_calc, args=(model_data,tuple(outcome),cds,x_bar_new,new_x_non_zero,time,btime)) for outcome in setlist]
			pool.close()
			pool.join()						
			
			
			alpha = sum(gk._value for gk in results)
			
							
			### Update terms
			
			x_bar = copy.deepcopy(x_bar_new)
			x_non_zero = copy.deepcopy(new_x_non_zero)
			
			
			
			
			itr += 1
			
		
			
		if itr == max_iterations:
			print('Maximum Iterations Reached')
			
		
		self.Upper_Bound = ENPV
	
		
	def _evaluate_ENPV(self,Decision_X,Decision_Z,model_data,sinf):
		### Build Box
		tbox = [0 for _ in range(len(model_data._data['time_step'][None]))]
		jbox = [copy.deepcopy(tbox) for _ in range(len(model_data._data['trial'][None]))]
		xbox = [copy.deepcopy(jbox) for _ in range(len(model_data._data['product'][None]))]
		zbox = [copy.deepcopy(jbox) for _ in range(len(model_data._data['product'][None]))]		
		
		
		for i in model_data._data['product'][None]:
			for j in model_data._data['trial'][None]:
				for t in model_data._data['time_step'][None]:
					xbox[model_data._data['product'][None].index(i)][model_data._data['trial'][None].index(j)][model_data._data['time_step'][None].index(t)] = round(Decision_X[i,j,t].value,6)
					zbox[model_data._data['product'][None].index(i)][model_data._data['trial'][None].index(j)][model_data._data['time_step'][None].index(t)] = round(Decision_Z[i,j,t].value,6)
		
		ENPV = self._Calculate_Value(xbox,zbox,model_data,sinf)
		
		return ENPV

	def _Calculate_Value(self, X, Z,model_data, sinf):
		### Use M2S Object to calculate parameters
		
		import Core.Solvers.MTSSP.M2S_item as M2S_item
		duration = model_data._data['trial_duration']
		gammaL = {}
		gammaD = {}
		revenue_max = {}
		prod = model_data._data['product'][None]
		sg = model_data._data['trial'][None]
		ts = model_data._data['time_step'][None]
		resource_type = model_data._data['resource_type'][None]
		
		trial_cost = model_data._data['trial_cost']
		
		success = M2S_item.calc_success(prod, len(sg), sinf)
		
		for items in model_data._data['gammaL']:
			gammaL[items[0]] = model_data._data['gammaL'][items]
			
		for items in model_data._data['gammaD']:
			gammaD[items[0]] = model_data._data['gammaD'][items]

		for items in model_data._data['maximum_revenue']:
			revenue_max[items[0]] = model_data._data['maximum_revenue'][items]
			
		last_trial = len(sg)
		
		## Calculate running rev
		rev_run = M2S_item.calc_rr(revenue_max,gammaL,duration, prod, sg, ts)
	
		##Calculate open rev
		rev_open = M2S_item.calc_openrev(revenue_max,gammaL,duration, prod, sg, ts, len(ts))

		##Calculate Discounting Factor
		discounting_factor = M2S_item.calc_discounting_factor(revenue_max,gammaL,trial_cost, prod, sg, len(ts))
		
		
			

		cost = sum((1 - 0.025 * (t - 1)) * trial_cost[(i,j)]*X[prod.index(i)][sg.index(j)][ts.index(t)] for i in prod for j in sg for t in ts)
		
		revenue =  sum( success[i] * revenue_max[i]*X[prod.index(i)][sg.index(last_trial)][ts.index(t)] for i in prod for t in ts) -  sum(success[i]*gammaD[i]*Z[prod.index(i)][sg.index(j)][ts.index(t)] for i in prod for j in sg if j>1 for t in ts) - sum(gammaL[i]*success[i]*(t + duration[(i,len(sg))])*X[prod.index(i)][sg.index(last_trial)][ts.index(t)] for i in prod for t in ts)
		
		FRV1 = sum(success[i] * rev_open[(i,j)] * discounting_factor[(i,j)] * Z[prod.index(i)][sg.index(j)][ts.index(len(ts))] for i in prod for j in sg)

		FRV2 = sum(success[i] * rev_run[(i,j,t)] * discounting_factor[(i,j+1)] * X[prod.index(i)][sg.index(j)][ts.index(t)] for i in prod for j in sg if j < last_trial for t in ts if t > len(ts) - duration[(i,j)])

		Free_revenue = FRV1 + FRV2
		
		
		value = revenue + Free_revenue - cost
		
		return value
		
	def _first_PH_mpfunc(self,model_data,Outcomes,btime,x_bar_z,cds,branch_probability_total,time):
		### Optimization things
		opt = SolverFactory("cplex")
		opt.options['threads'] = 6
		
		### Thread Specific Variables
		x_non_zero_t = []
		x_bar_thread = copy.deepcopy(x_bar_z)
		
		###  Generate non-scenario specific model variables
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
		
		Last_Time_Step = len(time_step)
		
		## Calculate running rev
		running_revenue = M2S_item.calc_rr(revenue_max,gammaL,duration, product, stage_gate, time_step)

		##Calculate open rev  
		open_revenue = M2S_item.calc_openrev(revenue_max,gammaL,duration, product, stage_gate, time_step, Last_Time_Step)

		##Calculate Discounting Factor
		discounting_factor = M2S_item.calc_discounting_factor(revenue_max,gammaL,trial_cost, product, stage_gate, Last_Time_Step)
		
		resource_max = {}
		for items in model_data._data['max_resource']:
			resource_max[items[0]] = model_data._data['max_resource'][items]
	
		resource_required = {}
		resource_required = model_data._data['resource_requirement']
		
		for OC in Outcomes:
			if OC != None:
				### Determine branch
				for b in self.Branches[time]:
					
					breal = 0
					for (i,j,real) in self.Branch_Def[b]:
						if OC[product.index(i)] + 1 > j and real == 1:
							breal += 1
						elif OC[product.index(i)] < j and real == 0:
							breal += 1
					
					if breal == len(self.Branch_Def[b]):
						sbranch = b
						break
			
			
				## Scenario Specific 
				sinf = SC.scenario(OC,model_data._data['probability'],product,model_data._data['trial'][None])
				
				Success = {}
				for i in product:
					Success[i] = sinf.success[product.index(i)]
				
				### Create Model
				model = MSSP.SingleScenario(product,stage_gate,time_step,resource_type,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,sinf.probability, Success,Last_Time_Step, last_trial, running_revenue, open_revenue, discounting_factor,OC)
				
				### Fix Decisions
							
				for t in self.Decisions[sbranch]:
					for (i,j,tm,tau,dec) in self.Decisions[sbranch][t]:
						model.Decision_X[i,j,tm + 1].value = dec
						model.Decision_X[i,j,t+1].fixed = True
				
				
				
				### Solve
				results = opt.solve(model)
				model.solutions.load_from(results)	
				
				
				### Record xbar --- abs is to get rid of negative zeros ??? 
				for (i,j,t) in cds[sbranch]:
					x_bar_thread[sbranch][product.index(i)][t-1] += sinf.probability/branch_probability_total[sbranch] * abs(model.Decision_X[i,j,t].value)
					
				
				### Record non-zero x's
				for (i,j,t) in cds[sbranch]:
					wval0 = 0
					dec1 = abs(model.Decision_X[i,j,t].value)
					x_non_zero_t.append((i,j,t,OC,wval0,dec1))
				
				del sbranch
	
		return [x_non_zero_t,x_bar_thread]	
		
	def _second_PH_mpfunc(self,model_data,Outcomes,btime,x_bar_z,cds,branch_probability_total,x_bar,x_non_zero,time,rho):
		### Optimization things
		opt = SolverFactory("cplex")
		opt.options['threads'] = 6
		
		
		### Thread Specific Variables
		x_non_zero_t = []
		x_bar_thread = copy.deepcopy(x_bar_z)
		tENPV = 0
	
		
		###  Generate non-scenario specific model variables
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
		
		Last_Time_Step = len(time_step)
		
		## Calculate running rev
		running_revenue = M2S_item.calc_rr(revenue_max,gammaL,duration, product, stage_gate, time_step)

		##Calculate open rev  
		open_revenue = M2S_item.calc_openrev(revenue_max,gammaL,duration, product, stage_gate, time_step, Last_Time_Step)

		##Calculate Discounting Factor
		discounting_factor = M2S_item.calc_discounting_factor(revenue_max,gammaL,trial_cost, product, stage_gate, Last_Time_Step)
		
		resource_max = {}
		for items in model_data._data['max_resource']:
			resource_max[items[0]] = model_data._data['max_resource'][items]
	
		resource_required = {}
		resource_required = model_data._data['resource_requirement']
		
		for OC in Outcomes:
			if OC != None:
				### Determine branch
				for b in self.Branches[time]:
				
					breal = 0
					for (i,j,real) in self.Branch_Def[b]:
						if OC[product.index(i)] + 1 > j and real == 1:
							breal += 1
						elif OC[product.index(i)] < j and real == 0:
							breal += 1
				
					if breal == len(self.Branch_Def[b]):
						sbranch = b
						break
						
				## Scenario Specific 
				sinf = SC.scenario(OC,model_data._data['probability'],product,model_data._data['trial'][None])
				
				Success = {}
				for i in product:
					Success[i] = sinf.success[product.index(i)]
				
				### Convert Xbar to Appropriate Format for Pyomo
				x_bar_func = {}
				w = {}
							
				for (i,j,t) in cds[sbranch]:
					x_bar_func[(i,j,t)] = x_bar[sbranch][product.index(i)][t-1]
				
				
				### Update w for the two cases
				
				### Case Non-Zero
				for (i,j,t,ss,wval0,dec1) in x_non_zero:
					if  ss == OC: 
						w[(i,j,t)] = wval0 + rho * (dec1 - x_bar[sbranch][product.index(i)][t-1])
																
				### Generate PH model
				model = MSSP.SS_PH(rho,w,x_bar_func,cds[sbranch],product,stage_gate,time_step,resource_type,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,sinf.probability, Success,Last_Time_Step, last_trial, running_revenue, open_revenue, discounting_factor,OC)
				
				
				### Fix Decisions
				for t in self.Decisions[sbranch]:
					for (i,j,tm,tau,dec) in self.Decisions[sbranch][t]:
						model.Decision_X[i,j,tm + 1].value = dec
						model.Decision_X[i,j,t+1].fixed = True
				
						
			
				### Solve
				results = opt.solve(model)
				model.solutions.load_from(results)	
				
				if str(results['Solver'][0]['Termination condition']) != 'optimal':
					print('Solution Not Optimal')
					print(results['Solver'][0]['Termination condition'])
							
				for (i,j,t) in cds[sbranch]:
					x_bar_thread[sbranch][product.index(i)][t-1] += sinf.probability/branch_probability_total[sbranch] * abs(model.Decision_X[i,j,t].value)
					
					
				### Update old non-zero x's
				for (i,j,t) in cds[b]:
					wval1 = w[(i,j,t)]
					dec1 = abs(model.Decision_X[i,j,t].value)
					x_non_zero_t.append((i,j,t,OC,wval1,dec1))
				
							
			
				### Calculate Equivalent ENPV for this scenario with the decisions
				tENPV += sinf.probability * self._evaluate_ENPV(model.Decision_X,model.Decision_Z,model_data,sinf)
				
				
		return [x_non_zero_t,x_bar_thread,tENPV]
	
	def _mp_gk_calc(self,model_data,Outcomes,cds,x_bar_new,new_x_non_zero,time,btime):
		gkt = 0
				
		for OC in Outcomes:
			if OC != None:
				# Determine Branch
				for b in self.Branches[time]:
					
					breal = 0
					for (i,j,real) in self.Branch_Def[b]:
						if OC[model_data._data['product'][None].index(i)] + 1 > j and real == 1:
							breal += 1
						elif OC[model_data._data['product'][None].index(i)] < j and real == 0:
							breal += 1
					
					if breal == len(self.Branch_Def[b]):
						sbranch = b
						break
						
				sinf = SC.scenario(OC,model_data._data['probability'],model_data._data['product'][None],model_data._data['trial'][None])
				sqrtterm = 0
				for (i,j,t) in cds[sbranch]:
					ltup = [tup for tup in new_x_non_zero if tup[0] == i and tup[1] == j and tup[2] == t and tup[3]==OC]
					if len(ltup) == 1:
						sqrtterm += (round(ltup[0][5],3) - round(x_bar_new[sbranch][model_data._data['product'][None].index(i)][t-1],3))**2
					else:
						print('ERROR!!!')
					
							
				gkt  += sinf.probability*sqrt(sqrtterm)
		return gkt
		
	def _grouper(self,ibl, n, fillvalue=None):
		args = [iter(ibl)]*n
		return itertools.zip_longest(fillvalue = fillvalue, *args)

import os
import sys
import itertools
import pdb
import time as timer

class KDA_results:
	def __init__(self, model_data, results, sp_realizations, output_directory):
		start_time = timer.clock()
		
		
		### Define Model Data
		self.model_data = model_data
		
		### Define realizations of trials
		self.sp_realizations = sp_realizations
		
		### Generate Scenario Set
		self.Scenario_Set = self.Define_Scenarios(output_directory)
		
		### Calculate X given decisions
		ENPV = 0
		
		
		import scenario_class as scenario_class
		prob = self.model_data._data['probability']
		
		cnt = 0
		
		with open(os.path.join(output_directory, 'KDA_Scenario_File')) as f:
			for line in f:
				line = line[:-1]
				line = tuple(int(x) for x in line[1:-1].split(','))
				
				s = scenario_class.scenario(line,prob, self.prod,self.sg)
				
				X = self.Calculate_X(results,s)
				
				Z = self.Calculate_Z(X,s)
			
				net_value = self.Calculate_Value(X,Z,s)
			
				probability = s.probability
			
				ENPV += probability * net_value
				cnt += 1
				
				if cnt % 1000 == 0:
					print str(cnt) 
							
		finish_time = timer.clock()
		self.Evaluation_Time = finish_time - start_time	
		self.ENPV = ENPV	
		
		
	
	def Define_Scenarios(self, output_directory):
		#### Problem Info For Scenario Generation
		
		num_product = len(self.model_data._data['product'][None])
		self.prod = self.model_data._data['product'][None]

		num_trial = len(self.model_data._data['trial'][None])
		self.sg = self.model_data._data['trial'][None]

		
		self.ts = self.model_data._data['time_step'][None]
		num_ts = len(self.model_data._data['time_step'][None])

		### Generate all possible outcomes
		SS = self.Write_Scenarios(output_directory, len(self.prod), range(num_trial +1))

		
		return SS
		
	def Write_Scenarios(self, output_directory, n, seq):
		### Generate New File Name
		save_file =  'KDA_Scenario_File' 
	
		### Open save file
		f = open(os.path.join(output_directory, save_file),	"w")
		
		NoScen = 0
		for p in itertools.product(seq, repeat=n):
			f.write("".join(str(p)))
			f.write("\n")
			NoScen += 1
		
		f.close()	
		return NoScen
        
			
	def Calculate_X(self, results, scenario):
		
		 ### Generate box to store results
		xbox = []
		for i in self.prod:
			jbox = []
			for j in self.sg:
				tbox = [0] * len(self.ts)
				jbox.append(tbox)
			xbox.append(jbox)
		
		t = 0 
		
		while t < len(self.ts):	 
			
							
			if t == 0:
		
				current_sp = '0'
				### The time zero decision is the same for all (root node sub-problem)
				for items in results[0]['0']:
					ii = self.model_data._data['product'][None].index(items[0])
					jj = self.model_data._data['trial'][None].index(items[1])
					xbox[ii][jj][0] = 1
				t += 1
		
			else:
				### Try to match the current SP
				try: 
					results[t]
					if current_sp in results[t]:
						for items in results[t][current_sp]:
							ii = self.model_data._data['product'][None].index(items[0])
							jj = self.model_data._data['trial'][None].index(items[1])
							xbox[ii][jj][t] = 1
						t += 1
						
					else:
					### If match use add decision
						searching = 1
						while searching == 1:
							for new_sp in results[t]:
								
								### IF no match, pop the entries (see if there was a realization)
								old_sp = new_sp.rsplit(".", 1)
								old_sp = old_sp[0]
								if current_sp == old_sp:
									matches = 0
							
									### If match, (should be min of two) see which sp_realization matches scenario outcome
									for selections in self.sp_realizations[new_sp]:
																			
										if scenario.outcome[selections[0]] > selections[1] and self.sp_realizations[new_sp][selections] == 1:
											matches += 1
										
										elif scenario.outcome[selections[0]] == selections[1] and self.sp_realizations[new_sp][selections] == 0:
											matches += 1
									
									
								
									if matches == len(self.sp_realizations[new_sp]):
										current_sp = new_sp
										for items in results[t][current_sp]:
											ii = self.model_data._data['product'][None].index(items[0])
											jj = self.model_data._data['trial'][None].index(items[1])
											xbox[ii][jj][t] = 1
										t += 1
									
										searching = 0
									
								
									
								
				except:
					t += 1
				
				
									
			
					
		return xbox
						
	def Calculate_Z(self,X,s):
		### Generate Zbox
		zbox = []
		for i in self.prod:
			jbox = []
			for j in self.sg:
				tbox = [0] * len(self.ts)
				jbox.append(tbox) 
			zbox.append(jbox)
			
		### First stage
		for i in self.prod:
			zbox[self.prod.index(i)][0][0] = 1 - X[self.prod.index(i)][0][0]
		
		
		
		### Other stages
		duration = self.model_data._data['trial_duration']
		
		for t in self.ts:
			for i in self.prod:
				for j in self.sg:
					indx = self.prod.index(i)
					jndx = self.sg.index(j)
					tndx = self.model_data._data['time_step'][None].index(t)
					if j > 1 and t - duration[(i,j-1)] > 0 and t  >  1 :
						pd = t- duration[(i,j-1)]
						zbox[indx][jndx][tndx] = zbox[indx][jndx][self.ts.index(t-1)] + X[indx][self.sg.index(j-1)][self.ts.index(pd)] - X[indx][jndx][tndx]
					elif t  >  1 and j > 1:
						zbox[indx][jndx][tndx] = zbox[indx][jndx][self.ts.index(t-1)] - X[indx][jndx][tndx]
					elif t==1 and j>1:
						zbox[indx][jndx][tndx] = - X[indx][jndx][tndx]
					elif t > 1 and jndx == 0:
						zbox[indx][0][tndx] = zbox[indx][0][self.ts.index(t-1)] - X[indx][0][tndx]
		return zbox

	def Calculate_Value(self, X, Z, s):
		### Use M2S Object to calculate parameters
		
		import Solvers.MTSSP.M2S_item as M2S_item
		duration = self.model_data._data['trial_duration']
		gammaL = {}
		gammaD = {}
		revenue_max = {}
						
		resource_type = self.model_data._data['resource_type'][None]
		
		trial_cost = self.model_data._data['trial_cost']
		
		success = M2S_item.calc_success(self.prod, len(self.sg), s)
		
		for items in self.model_data._data['gammaL']:
			gammaL[items[0]] = self.model_data._data['gammaL'][items]
			
		for items in self.model_data._data['gammaD']:
			gammaD[items[0]] = self.model_data._data['gammaD'][items]

		for items in self.model_data._data['maximum_revenue']:
			revenue_max[items[0]] = self.model_data._data['maximum_revenue'][items]
			
		last_trial = self.sg[-1]
		
		## Calculate running rev
		rev_run = M2S_item.calc_rr(revenue_max,gammaL,duration, self.prod, self.sg, self.ts)
	
		##Calculate open rev
		rev_open = M2S_item.calc_openrev(revenue_max,gammaL,duration, self.prod, self.sg, self.ts, len(self.ts))

		##Calculate Discounting Factor
		discounting_factor = M2S_item.calc_discounting_factor(revenue_max,gammaL,trial_cost, self.prod, self.sg, len(self.ts))

		cost = sum((1 - 0.025 * (t - 1)) * trial_cost[(i,j)]*X[self.prod.index(i)][self.sg.index(j)][self.ts.index(t)] for i in self.prod for j in self.sg for t in self.ts)
		
		revenue =  sum( success[i] * revenue_max[i]*X[self.prod.index(i)][self.sg.index(last_trial)][self.ts.index(t)] for i in self.prod for t in self.ts) -  sum(success[i]*gammaD[i]*Z[self.prod.index(i)][self.sg.index(j)][self.ts.index(t)] for i in self.prod for j in self.sg if j>1 for t in self.ts) - sum(gammaL[i]*success[i]*(t + duration[(i,len(self.sg))])*X[self.prod.index(i)][self.sg.index(last_trial)][self.ts.index(t)] for i in self.prod for t in self.ts)
		
		FRV1 = sum(success[i] * rev_open[(i,j)] * discounting_factor[(i,j)] * Z[self.prod.index(i)][self.sg.index(j)][self.ts.index(len(self.ts))] for i in self.prod for j in self.sg)

		FRV2 = sum(success[i] * rev_run[(i,j,t)] * discounting_factor[(i,j+1)] * X[self.prod.index(i)][self.sg.index(j)][self.ts.index(t)] for i in self.prod for j in self.sg if j < last_trial for t in self.ts if t > len(self.ts) - duration[(i,j)])

		Free_revenue = FRV1 + FRV2
		
		
		value = revenue + Free_revenue - cost
		
		
		return value

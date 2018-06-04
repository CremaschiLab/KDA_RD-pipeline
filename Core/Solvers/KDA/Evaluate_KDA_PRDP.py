import os
import sys
import itertools
import pdb
import time as timer
import multiprocessing as mp
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))
import MTSSP.M2S_item as M2S_item
import MSSP.scenario_class as scenario_class
from ctypes import c_double

class KDA_PRDP_results:
	def __init__(self, model_data, results, sp_realizations, output_directory):
		start_time = timer.clock()
		process_count = mp.cpu_count()
		
		### Define Lock and Locked Value
		ENPV_Counter = mp.Value(c_double, 0)
		ENPV_Lock = mp.Lock()	
		
		### Generate 
		seq = len(model_data._data['product'][None])
		n = len(model_data._data['trial'][None]) + 1
		n = range(n)
		list_of_outcomes = itertools.product(n, repeat = seq)
		np = int(math.ceil(list_of_outcomes.__sizeof__() / float(process_count)))
		setlist = grouper(list_of_outcomes,np)
		
		### Create Pool
		pool = mp.Pool(process_count, initializer, (ENPV_Counter,ENPV_Lock))
		
		results = [pool.apply_async(Parallel_Evaluate_KDA_PRDP, args=(tuple(outcome), model_data,sp_realizations,results)) for outcome in setlist]
		pool.close()
		pool.join()
							
		finish_time = timer.clock()
		self.Evaluation_Time = finish_time - start_time	
		self.ENPV = ENPV_Counter.value	
		
def IncrementENPV(ENPV):
	with ENPV_Lock:
		ENPV_Counter.value += ENPV
		
def initializer(*args):
	global ENPV_Counter, ENPV_Lock
	ENPV_Counter, ENPV_Lock = args

		
def Parallel_Evaluate_KDA_PRDP(outcome,model_data,sp_realizations,results):	
	ENPV = 0
	for oc in outcome:
		if oc == None:
			pass
		else:
			s = scenario_class.scenario(oc,model_data._data['probability'], model_data._data['product'][None],model_data._data['trial'][None])
				
			X = Calculate_X(results, model_data, sp_realizations,s)
				
			Z = Calculate_Z(X,model_data,s)
			
			net_value = Calculate_Value(X,Z,model_data,s)
			
			probability = s.probability
	
			ENPV += probability * net_value
		
	IncrementENPV(ENPV)
	     
			
def Calculate_X(results, model_data, sp_realizations, scenario):
	prod = model_data._data['product'][None]
	sg = model_data._data['trial'][None]
	ts = model_data._data['time_step'][None]
		
	### Generate box to store results
	xbox = []
	for i in prod:
		jbox = []
		for j in sg:
			tbox = [0] * len(ts)
			jbox.append(tbox)
		xbox.append(jbox)
		
	t = 0 
		
	while t < len(ts):	 
			
							
		if t == 0:
		
			current_sp = '0'
			### The time zero decision is the same for all (root node sub-problem)
			for items in results[0]['0']:
				ii = model_data._data['product'][None].index(items[0])
				jj = model_data._data['trial'][None].index(items[1])
				xbox[ii][jj][0] = 1
			t += 1
		
		else:
			### Try to match the current SP
			try: 
				results[t]
				if current_sp in results[t]:
					for items in results[t][current_sp]:
						ii = model_data._data['product'][None].index(items[0])
						jj = model_data._data['trial'][None].index(items[1])
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
								for selections in sp_realizations[new_sp]:
																			
									if scenario.outcome[selections[0]] > selections[1] and sp_realizations[new_sp][selections] == 1:
										matches += 1
										
									elif scenario.outcome[selections[0]] == selections[1] and sp_realizations[new_sp][selections] == 0:
										matches += 1
									
									
								
								if matches == len(sp_realizations[new_sp]):
									current_sp = new_sp
									for items in results[t][current_sp]:
										ii = model_data._data['product'][None].index(items[0])
										jj = model_data._data['trial'][None].index(items[1])
										xbox[ii][jj][t] = 1
									t += 1
									
									searching = 0
									
								
									
								
			except:
				t += 1
				
				
									
			
					
	return xbox
						
def Calculate_Z(X,model_data,s):
	prod = model_data._data['product'][None]
	sg = model_data._data['trial'][None]
	ts = model_data._data['time_step'][None]
	
	### Generate Zbox
	zbox = []
	for i in prod:
		jbox = []
		for j in sg:
			tbox = [0] * len(ts)
			jbox.append(tbox) 
		zbox.append(jbox)
			
	### First stage
	for i in prod:
		zbox[prod.index(i)][0][0] = 1 - X[prod.index(i)][0][0]
		
		
		
	### Other stages
	duration = model_data._data['trial_duration']
		
	for t in ts:
		for i in prod:
			for j in sg:
				indx = prod.index(i)
				jndx = sg.index(j)
				tndx = model_data._data['time_step'][None].index(t)
				if j > 1 and t - duration[(i,j-1)] > 0 and t  >  1 :
					pd = t- duration[(i,j-1)]
					zbox[indx][jndx][tndx] = zbox[indx][jndx][ts.index(t-1)] + X[indx][sg.index(j-1)][ts.index(pd)] - X[indx][jndx][tndx]
				elif t  >  1 and j > 1:
					zbox[indx][jndx][tndx] = zbox[indx][jndx][ts.index(t-1)] - X[indx][jndx][tndx]
				elif t==1 and j>1:
					zbox[indx][jndx][tndx] = - X[indx][jndx][tndx]
				elif t > 1 and jndx == 0:
					zbox[indx][0][tndx] = zbox[indx][0][ts.index(t-1)] - X[indx][0][tndx]
	return zbox

def Calculate_Value(X, Z, model_data, s):
	### Use M2S Object to calculate parameters
	prod = model_data._data['product'][None]
	sg = model_data._data['trial'][None]
	ts = model_data._data['time_step'][None]	
		
	duration = model_data._data['trial_duration']
	gammaL = {}
	gammaD = {}
	revenue_max = {}
						
	resource_type = model_data._data['resource_type'][None]
		
	trial_cost = model_data._data['trial_cost']
		
	success = M2S_item.calc_success(prod, len(sg), s)
		
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

def grouper(iterable, n, fillvalue=None):
	args = [iter(iterable)]*n
	return itertools.zip_longest(fillvalue = fillvalue, *args)

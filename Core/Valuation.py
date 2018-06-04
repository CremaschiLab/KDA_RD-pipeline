import os
import sys
import pdb

def valuation(xbox, prod, sg, ts, SS, List_of_Scenarios, duration, trial_cost, success, discounting_factor, gammaD, gammaL, rev_max, last_trial, rev_open, rev_run, num_ts, last_time_step ):
	## Calculate z(i,j,t,s)
	print("Valuation Initiallized")
	zbox = {}
	for items in SS:
		print(str(items))
		ibox = []
		for i in prod:
			jbox = []
			for j in sg:
				tbox = [0] * num_ts
				jbox.append(tbox) 
			ibox.append(jbox)
		zbox[items] = ibox
		
	print("Calculating Z")
	for i in prod:
		for s in SS:
			zbox[s][prod.index(i)][0][0] = 1 - xbox[s][prod.index(i)][0][0]
			
	for i in prod:
		for t in ts:
			for s in SS:
				if t > 1:
					zbox[s][prod.index(i)][0][ts.index(t)] = zbox[s][prod.index(i)][0][ts.index(t-1)] - xbox[s][prod.index(i)][0][ts.index(t)]
		
	
	for t in ts:
		for i in prod:
			for j in sg:
				for s in SS:
					indx = prod.index(i)
					jndx = sg.index(j)
					tndx = ts.index(t)
					if j > 1 and t- duration[(i,j-1)] > 0 and t  >  1 :
						pd = t- duration[(i,j-1)]
						zbox[s][prod.index(i)][sg.index(j)][ts.index(t)] = zbox[s][prod.index(i)][sg.index(j)][ts.index(t-1)] + xbox[s][prod.index(i)][sg.index(j-1)][ts.index(pd)] - xbox[s][prod.index(i)][sg.index(j)][ts.index(t)]
					elif t  >  1 and j > 1:
						zbox[s][prod.index(i)][sg.index(j)][ts.index(t)] = zbox[s][prod.index(i)][sg.index(j)][ts.index(t-1)] - xbox[s][prod.index(i)][sg.index(j)][ts.index(t)]
					elif t==1 and j>1:
						zbox[s][prod.index(i)][sg.index(j)][ts.index(t)] = - xbox[s][prod.index(i)][sg.index(j)][ts.index(t)]


	cost = {}
	revenue = {}
	Free_revenue = {}
	FRV1 = {}
	FRV2 = {}
	value = {}
	NPV={}
	
	
	## Calculate costs for each scenario
	for s in SS:
		print(str(s))
		cost[s] = sum((1 - 0.025 * (t - 1)) * trial_cost[(i,j)]*xbox[s][prod.index(i)][sg.index(j)][ts.index(t)] for i in prod for j in sg for t in ts)
		
	## Calculate the revenue for each scenario
		revenue[s] =  sum( success[(i,s)] * rev_max[i]*xbox[s][prod.index(i)][sg.index(last_trial)][ts.index(t)] for i in prod for t in ts) -  sum(success[(i,s)]*gammaD[i]*zbox[s][prod.index(i)][sg.index(j)][ts.index(t)] for i in prod for j in sg if j>1 for t in ts) - sum(gammaL[i]*success[(i,s)]*(t + duration[(i,last_trial)])*xbox[s][prod.index(i)][sg.index(last_trial)][ts.index(t)] for i in prod for t in ts)
		
	## Calculate Free Revenue
		FRV1[s] = sum(success[(i,s)] * rev_open[(i,j)] * discounting_factor[(i,j)] * zbox[s][prod.index(i)][sg.index(j)][ts.index(last_time_step)] for i in prod for j in sg)

		FRV2[s] = sum(success[(i,s)] * rev_run[(i,j,t)] * discounting_factor[(i,j+1)] * xbox[s][prod.index(i)][sg.index(j)][ts.index(t)] for i in prod for j in sg if j < last_trial for t in ts if t > last_time_step - duration[(i,j)])

		Free_revenue[s] = FRV1[s] + FRV2[s]
		
		value[s] = revenue[s] + Free_revenue[s] - cost[s]

	
	ENPV = 0

	for s in SS:
		NPV[s] = value[s]
		ENPV += List_of_Scenarios[s].probability * value[s]

	return ENPV



	

	

			


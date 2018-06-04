import os
import sys
import pdb

class scenario:
	def __init__(self,outcome,prob,product, trial):
		self.outcome = outcome
		self.probability = self.calc_probability(outcome,prob, product, trial)
		self.calc_success(trial)

	def calc_probability(self,outcome, prob, product, trial):
		p = 1
		i = 0
		while i < len(outcome):
			if outcome[i] == len(trial):
				for j in trial:
					coords = (product[i],j)
					p *= prob[coords]
			else:
				for j in trial:
					tindex = trial.index(j)
					coords = (product[i],trial[tindex])
					if tindex < outcome[i]:
						p *= prob[coords]
					elif tindex == outcome[i]:
						p *= (1 - prob[coords])
			i += 1
		return p

	def calc_success(self,trial):
		self.success = [0]*len(self.outcome)
		i=0
		while i < len(self.outcome):
			if self.outcome[i] == len(trial):
				self.success[i] = 1
			else:
				self.success[i] = 0
				
			i +=1


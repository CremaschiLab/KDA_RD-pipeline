import os
import sys
import pdb

class scenario:
	def __init__(self,outcome,prob,product, trial):
		self.outcome = outcome
		self.probability = self.calc_probability(outcome,prob, product, trial)

	def calc_probability(self,outcome, prob, product, trial):
		p = 1
		i = 0
		while i < len(outcome):
			if outcome[i] == len(trial) + 1:
				for j in trial:
					coords = (product[i],trial[tindex])
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


				


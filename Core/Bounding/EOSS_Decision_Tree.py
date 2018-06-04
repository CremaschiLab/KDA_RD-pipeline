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
			(i,j,t,rlzn)
		"""
		if old_tree == {}:
			### Initialize Structures
			self.Decision = {}
		
			### Define UB Initializations
			self.Upper_Bound = float('nan')
			
			
		else:
			self.Decision = copy.deepcopy(old_tree.Decision)
			self.Upper_Bound = copy.deepcopy(old_tree.Upper_Bound)
			
	def __repr__(self):
		return str(self.Upper_Bound)
		
	def add_decision(self,MD,dec,rlzn, OD):
		"""
		Decision- (i,j,t,Decision[0,1])
		Realization- [(i,j,Realization[0,1])] associated with decision
		"""
		for d in dec:
			try:
				self.Decision[d].append(set(rlzn))
			except:
				self.Decision[d] = []
				self.Decision[d].append(set(rlzn))
			
		### Update Upper Bound
		self.Upper_Bound = self.EOSS_Update(MD,OD,dec)
	
	def EOSS_Update(self,MD, OD,dec):
		import Core.Solvers.EOSS.EOSSBound as Solve
		Results = Solve.EOSS_PRDP_Solve(MD,self.Decision)
		if Results > self.Upper_Bound:
			save_file =  "Solver" + "_" + "Error"
			## write a file with error results
			f = open(os.path.join(OD, save_file),	"a")
			f.write('\n')
			err = "Upper bound increased from " + str(self.Upper_Bound) + " to " + str(Results)
			decs = "Added decisions were " + str(dec) + " with " + str(self.Decision)
			f.write(err + '\n')
			f.write(decs)
			f.write('\n')
			f.close()
			
		return Results

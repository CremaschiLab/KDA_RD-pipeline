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
		self.Upper_Bound = self.Bound_Update(MD,OD,dec)
		
	def Bound_Update(self.MD,OD,dec):
		import Core.Solvers.PH.PH_Bound_Generator as Solve
		self.Upper_Bound = Solve(MD,dec)

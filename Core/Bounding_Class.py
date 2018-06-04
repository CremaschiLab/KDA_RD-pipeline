import os
import sys
import pdb

class Bkda:
	def __init__(self,Evaluated_Solution,Solution):
		self.ENPV = Evaluated_Solution.ENPV
		self.Results = Solution.output['results']
		self.Realizations = Solution.output['sub_problem_realizations']
		self.Problem_Count = Solution.output['problem_count']
		self.Solve_Time = Solution.output['algorithm_time']
	
	def __repr__(self):
		return self.ENPV

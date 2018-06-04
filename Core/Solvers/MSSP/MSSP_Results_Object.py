import sys
import os


class MSSP_Results_Object:
	
	def __init__(self,ENPV,Solve_Time, Resource_Usage,Total_Time):
		self.ENPV = ENPV
		self.Solve_Time = Solve_Time
		self.Resource_Usage = Resource_Usage
		self.Total_Time = Total_Time
	
	def __repr__(self):
		return self.ENPV

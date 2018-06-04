import os
import sys
import pdb
from Core.Solvers.MTSSP import PRDP_Data_Processing

class MTSSP_Data_Processing:
	def __init__(self, model_data):
		
		### self attributes
		self._model_data = model_data._data
		self.model_type = self._model_data['model_type'][None][0]
		
		### determine which sub-routine to use for each model type
		if self.model_type == 'PRDP':
			self.Parameters = self.MTSSP_PRDP()
		else:
			raise Exception("Supported model type not set in model file") 
	
	def MTSSP_PRDP(self):
		
		### Calculate and Assign Values for the Return Variable and Scenario Sets
		problem_data = PRDP_Data_Processing.MTSSP_PRDP_Data_Processing(self._model_data)
		
		return problem_data	
	
def MTSSP_Realization(model_type, scenario_set, model_data):
	
	### Routing block for each model type
	if model_type == 'PRDP':
		intermediate = PRDP_Data_Processing.PRDP_Realization(model_data, scenario_set, results, ts)

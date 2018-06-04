import os
import sys

def det_inits(results, model_type, model_data, output_directory, mipgap):
	if model_type == 'PRDP':
		import PRDP_DI 
		PRDP_Out = PRDP_DI.warmstart_class(model_data, results, output_directory, mipgap)
	else:
		raise Exception("Model type not currently supported")
		
		

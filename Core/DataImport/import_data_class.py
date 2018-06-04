import os
import sys
from . import parse_data_cmds
import pdb

class Data_Collection:
	def __init__(self, optcmd, **kwgs):
		self._data = {}
		self._dimension1 = {}
		self._param_items = {}
		self._read_file(optcmd)
		self._data_handling()

	def _read_file(self, optcmd, **kwgs):
		"""
		The following function reads in the raw data files by calling ply.lex. The model_type
	 	requirement is necessary to make sure the data parse command uses the correct lex
	 	supplementary files
		""" 
		filename = optcmd[1]
			## This portion uses the imported parse data commands to parse the text document. 
			##  The parse data commands contains the supporting lex and yacc definitions and
			## declarations.			
		pdb.set_trace
		try:
			self._raw_data = parse_data_cmds.parse_data_commands(filename= filename)
		except IOError:
			raise IOError("Error: Unable to Parse File")
		if self._raw_data is None:
			return False	 
	
		return True

	def _data_handling(self, **kwgs):
		""" 
		The following function takes the raw data and breaks it into parameter/set chunks to process further
		"""
		for item in self._raw_data:
			for datcmd in self._raw_data[item]:
				if item not in self._data:
					self._data[item] = {}
				if datcmd[0] in ('include', 'import', 'load'):
					self._tmpdata = {}
					self._data_processing(datcmd)
					if item is None:
						for key in self._tempdata:
							if key in _data:
								self._data[key].update(self._tempdata[key])
							else:
								self._data[key] = self._tmpdata[key]
					else:	
						for key in self._tmpdata:
							if key in None:
								self._data[item].update(self._tmpdata[key])
							else:
								raise IOError("Error: Cannot define scenario within another scenario")
				else:
					 self._data_processing(datcmd)
		

	def _data_processing(self, datcmd):
		"""
		This function routes the pieces of data for pre-processing and to the appropriate type processing
		"""
		if len(datcmd) == 0:
			raise ValueError("Error: Empty list passes to process")
		
		datcmd = self._preprocess_data(datcmd)
		if datcmd[0] == 'set':
			self._process_set(datcmd)
		elif datcmd[0] == 'param':
			self._process_param(datcmd)
		else:
			IOError("Error: Unknown command given.")

		return True
    	

	def _preprocess_data(self, datcmd):
		"""
		The following function removes the parenteses from the data that was read in
		"""

		status=")"
		newcmd=[]
		for token in datcmd:
			if type(token) == str:
				token=str(token)
				if "(" in token and ")" in token:
					newcmd.append(token)
					status=")"
				elif "(" in token:
					if status == "(":
						raise ValueError("Two '('s follow each other in data" + token)
					status=")"
					newcmd[-1] = newcmd[-1] + token
				elif ")" in token:
					if status == ")":
						raise ValueError("Two ')'s follow each other in data" + token)
					status=")"
					newcmd[-1] = newcmd[-1] + token
				elif status == "(":
					newcmd[-1] = newcmd[-1] + token
				else:
					newcmd.append(token)
			else:
				if type(token) is float and math.floor(token) == token:
					token=int(token)
				newcmd.append(token)					
		return newcmd

	def _process_set(self, datcmd):
		"""
		The following types and sorts a set of data
		"""
		if datcmd[2] != ':=':
			raise ValueError("Error: Set format exception")

		self._data[datcmd[1]] = {}
				
		set_items = datcmd[3:]
		set_name = datcmd[1]

		set_items = self._data_eval(set_items)
		index = 0
		ans = []

		while index < len(set_items):
			ans.append(set_items[index])
			index += 1

		self._data[set_name][None] = ans
		

	def _process_param(self, datcmd):
		"""
		Processes parameters that are predefined by model
		"""
		if datcmd[2] == ':':
			param_name = datcmd[1]
			cutcmd = datcmd[3:]
			i = 0
			while i < len(cutcmd):
				if cutcmd[i] == ':=':
					values_expected = i
					break
				i += 1
			dimension1 = self._data_eval(cutcmd[0:(values_expected)])
			self._dimension1[param_name] = dimension1
			param_items = self._data_eval(cutcmd[(values_expected+1):])
			self._param_items[param_name] = param_items
			if param_name not in self._data:
				self._data[param_name] = {}
			j = 0
			while j < len(param_items):
				k = 0
				while k < len(dimension1):
					key = (dimension1[k],param_items[j])
					self._data[param_name][key] = param_items[k+j+1]
					k += 1
				j += len(dimension1) + 1

		elif datcmd[2] == ':=':
			param_name = datcmd[1]
			dimen = self._dim(param_name)
			cutcmd = self._data_eval(datcmd[3:])
			if param_name not in self._data:
				self._data[param_name] = {}
			j = 0
			while j < len(cutcmd):
				key = tuple(cutcmd[j:(j + dimen)])
				self._data[param_name][key] = cutcmd[j + dimen]
				j = j + dimen + 1

		else:
			raise ValueError("Error: Parameter format incorrect.")


		
	def _data_eval(self, values):
		"""
		Evaluate the list of values to make them bool, integer or float, or a tuple value.
		"""
		try:
			unicode
		except:
			unicode = str
		try:
			long
			numlist = (bool, int, float, long)
		except:
			numlist = (bool, int, float)

		ans = []
		for val in values:
			if type(val) in numlist:
				ans.append(val)
				continue
			if val in ('True','true','TRUE'):
				ans.append(True)
				continue
			if val in ('False','false','FALSE'):
				ans.append(False)
				continue
			if type(val) is tuple:
				vals = []
				for item in val:
					vals.append( _data_eval([item])[0] )
				ans.append(tuple(vals))
				continue
			tmp = None
			tval = val.strip()
			if (tval[0] == "(" and tval[-1] == ")") or (tval[0] == '[' and tval[-1] == ']'):
				vals = []
				tval = tval[1:-1]
				for item in tval.split(","):
					tmp=_data_eval([item])
					vals.append(tmp[0])
				ans.append(tuple(vals))
				continue
			try:
				tmp = int(val)
				ans.append(tmp)
			except ValueError:
				pass
			if tmp is None:
				try:
					tmp = float(val)
					ans.append(tmp)
				except ValueError:
					if val[0] == "'" or val[0] == '"':
						ans.append(val[1:-1])
					else:
						ans.append(val)
		return ans

		
	def _dim(self, param_name):
		if param_name == 'trial_cost':
			dim = 2
		elif param_name == 'trial_duration':
			dim = 2
		elif param_name == 'resource_requirement':
			dim = 3
		elif param_name == 'maximum_revenue':
			dim = 1
		elif param_name == 'probability':
			dim = 2
		elif param_name == 'gammaL':
			dim = 1
		elif param_name == 'gammaD':
			dim = 1
		elif param_name == 'max_resource':
			dim = 1
		elif param_name == 'model_type':
			dim = 1
		else:
			raise ValueError("Error: Unknown parameter")
		return dim

	

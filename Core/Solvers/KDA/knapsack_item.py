import os
import sys
import pdb

class knapsack_data_processing:
	def __init__(self, data):
		self._data = data._data
		self.item_set = {}
		self.items = {}
		self.ItemList = []
		products = data._data['product'][None]
		trials = data._data['trial'][None]
		counter = 1
		for i in products:
			for j in trials:
				item_coordinates_product = products.index(i)
				item_coordinates_trial = trials.index(j)
				item_coordinates = (item_coordinates_product, item_coordinates_trial)
				item_name = "Item" + str(counter)
				self.ItemList.append(item_name)
				self.items[item_name] = item_coordinates
				item = self.knapsack_item_values(item_coordinates, item_name) 
				self.item_set[item_name] = item
				counter += 1
				
		
	def knapsack_item_values(self, coords, item_name):
		
		## Variables to calulate
		self.coords = coords
		self.item_name = item_name
		self.product = self._data['product'][None][coords[0]]
		item_information = {}
		
		## Calculate item weight
		item_weight = self._process_item_weight()
		item_information['item_weight'] = item_weight

		## Calculate item value
		item_value = self._process_item_value()
		item_information['item_value'] = item_value

		##Calculate remaining time
		remaining_time = self._calculate_remaining_time()
		item_information['remaining_time'] = remaining_time	
	
		## Calculate mu
		mu = self._item_mu()
		item_information['mu'] = mu	
		
		## Calculate probabilistic mu
		prob_mu = self._item_prob_mu()
		item_information['probmu'] = prob_mu
		
		## Calculate Probability
		probability = self._item_probability()
		item_information['probability'] = probability
		
		### Calculate item coordinates
		item_information['coords'] = coords
		
		### Calculate remaining resources
		remaining_resources = self._calculate_resources_remaining()
		item_information['resources_remaining'] = remaining_resources
		
		return item_information

	def _process_item_weight(self):
		##The item weight is the a function of the resource type and is 
		item_weight = {}
		for resourcetype in self._data['resource_type'][None]:
			j = self._data['trial'][None][self.coords[1]]
			key = (self.item_name, resourcetype)
			key2 = (self.product, j,resourcetype)
			try:
				item_weight[key] = self._data['resource_requirement'][key2]
			except:
				raise ValueError("Error: Model Data not fully specified")
		return item_weight

	def _calculate_cdt_mod(self,trial):
		#
		#This portion calculates the cdtmod function which discounts the subsequent trials in the item
		#
		j = 0
		tauprime = 0
		while j < trial:
			trial = self._data['trial'][None][j]
			key = (self.product, trial)
			tauprime += self._data['trial_duration'][key]
			j += 1
		cdtmod = 1 - .025 * tauprime
		return cdtmod
	
	def _process_item_value(self):
		#
		#Find the cost of running all the trials that occur by starting the trial with the given coordinates 
		#
		cost = 0
		
		for j in self._data['trial'][None]:
			if j == self._data['trial'][None][self.coords[1]]:
				key = (self.product,j)
				cost += self._data['trial_cost'][key]
			elif j <= len(self._data['trial'][None]) and j > self.coords[1]:
				CDTmod = self._calculate_cdt_mod(j)
				key = (self.product,j)
				cost += CDTmod * self._data['trial_cost'][key]
			else:
				pass
			
			

		#
		# This finds the revenue possible for each item
		#
		key2 = (self.product,)
		revenue = self._data['maximum_revenue'][key2]
		value = revenue - cost
		return value

	def _item_probability(self):
		j = 0
		probability = 1
		last_item = self._data['trial'][None][-1]
		while j < len(self._data['trial'][None]):
			if j <= self._data['trial'][None].index(last_item) and j >= self.coords[1]:
				trial = self._data['trial'][None][j]
				key = (self.product, trial)
				probability *= self._data['probability'][key]
			else:
				pass
			j += 1
		return probability	

	def _item_mu(self):
		dummy = {}
		
		for index in self._data['resource_type'][None]:
			mu = 0
			for trials in self._data['trial'][None]:
				if self._data['trial'][None].index(trials) >= self.coords[1]:
					dummy_coords = self._data['trial'][None].index(trials)
					key = (self.product,self._data['trial'][None][dummy_coords],index)
					key3 = (self.product,self._data['trial'][None][dummy_coords])
					calc = (self._data['resource_requirement'][key] * self._data['trial_duration'][key3] )
					mu += calc
				else:
					pass
			key2 = (self.item_name, index)
			dummy[key2] = float(mu)
		return dummy
		
	def _item_prob_mu(self):		
		dummy = {}
		
		for resource in self._data['resource_type'][None]:
			mu = 0
			for trial in self._data['trial'][None]:
				if self._data['trial'][None].index(trial) >= self.coords[1]:
					trial_index = self._data['trial'][None].index(trial)
					resource_key = (self.product,self._data['trial'][None][trial_index],resource)
					duration_key = (self.product,self._data['trial'][None][trial_index])
					if self._data['trial'][None].index(trial) == self.coords[1]:	
						calc = (self._data['resource_requirement'][resource_key] * self._data['trial_duration'][duration_key])
						mu += calc
					else:
						tmpprob = 1
						for trl in self._data['trial'][None]:
							if trl > self.coords[1] and trl < trial:
								tmpprob = tmpprob * self._data['probability'][(self.product,trl)]
						calc = (self._data['resource_requirement'][resource_key] * self._data['trial_duration'][duration_key] * tmpprob)
						mu += calc
				else:
					pass
			key2 = (self.item_name, resource)
			dummy[key2] = float(mu)
		return dummy

	def _calculate_remaining_time(self):
		product = self._data['product'][None][self.coords[0]]
		trial = self._data['trial'][None][self.coords[1]]
		time_remaining = 0
		for j in self._data['trial'][None]:
			
			if self._data['trial'][None].index(j) >= self.coords[1]:
				key = (product,j)
				time_remaining += self._data['trial_duration'][key]
			else:
				pass
		return time_remaining
	
	def _calculate_resources_remaining(self):
		product = self._data['product'][None][self.coords[0]]
		trial = self._data['trial'][None][self.coords[1]]
		resources_remaining = {}
		for r in self._data['resource_type'][None]:
			resources_remaining[r] = 0
			for j in self._data['trial'][None]:
				if self._data['trial'][None].index(j) >= self.coords[1]:
					key = (product,j,r)
					resources_remaining[r] += self._data['resource_requirement'][key]
		return resources_remaining
				
class Item_Selection:
	def __init__(self, time, Item_Name, Item_Coords, Item_Duration):
		self.COORDS = Item_Coords
		self.isstarted = time
		self.isfinished = time + Item_Duration
		self.ITEM_NAME	= Item_Name				
			
			

		

		


import sys
import os
import pdb

def initial_existance(knapsack_data):
	ex = {}
	for index in knapsack_data.ItemList:
		if knapsack_data.items[index][1] == 0:
			ex[index] = 1
		else:
			ex[index] = 0
	return ex

def initial_fixed_parameters(fixed_parameters, knapsack_data, model_data):
	fixed_items = []
	### Loop over all the items in fixed parameters
	for (i,j,t,dec) in fixed_parameters:
		
		### If the time component matches 
		if t == 0:
			
			### Determine the corresponding Item
			products = model_data._data['product'][None]
			trials = model_data._data['trial'][None]
			
			product_coordinate = products.index(i)
			trial_coordinate = trials.index(j)
			
			corresponding_item_coordinates = (product_coordinate, trial_coordinate)
			
			### Loop over all the items to find the coordinates for the selected item
			for itm in knapsack_data.ItemList:
				if knapsack_data.items[itm] == corresponding_item_coordinates:
					fix_item = (itm, dec)
					fixed_items.append(fix_item)
			
	return fixed_items
					
def PRDP_Max_Solve_Model_Generator(knapsack_data, model_data, existance, sub_problem, time, max_duration, _opts, penval):
	
	####################################################################
	### 					Define Parameters
	####################################################################
	v = {}
	w = {}
	w_max = {}
	mu = {}

	## Set known parameters that are consistant for all instances
	items = knapsack_data.ItemList

	## Set the values for resource type
	resources = model_data._data['resource_type'][None]

	## Set the weight of each item. This should be the trial resource requirements
	for index in knapsack_data.ItemList:	
		w.update(knapsack_data.item_set[index]['item_weight'])
	
	## Set the maximum number of resources available of each type
	for index in model_data._data['resource_type'][None]:
		w_max[index] = model_data._data['max_resource'][(index,)]

	## Set mu. Mu is the amount of each resource remaining to complete all trials
	if 'probabilistic' in _opts:
		for index in knapsack_data.ItemList:
			mu.update(knapsack_data.item_set[index]['probmu'])
	else:	
		for index in knapsack_data.ItemList:
			mu.update(knapsack_data.item_set[index]['mu'])
	
	### Set Time Specific Value for all items
	for index in knapsack_data.ItemList:
				
		### Determine product
		product = model_data._data['product'][None][knapsack_data.items[index][0]]
				
		### Get the undepreciated value
		undepreciated_value = knapsack_data.item_set[index]['item_value']
				
		### set the time remaining
		time_remaining = knapsack_data.item_set[index]['remaining_time']
				
		### Set the probability of passing
		probability = knapsack_data.item_set[index]['probability']
				
		### Depreciate the undepreciated value
		depreciated_value = probability *(undepreciated_value - model_data._data['gammaL'][(product,)] * ( time + 1 + time_remaining))
				
		### Set the value
		v[index] = depreciated_value	
				
		### Determine Max Duration Parameter
			
		if existance[(sub_problem,time)][index] == 1:
					
			### Get item coords
			product = model_data._data['product'][None][knapsack_data.items[index][0]]
			trial = model_data._data['trial'][None][knapsack_data.items[index][1]]
					
			### Get item key	
			key = (product,trial)
					
			### Calculate the duration needed to finish
			nduration = time_remaining + model_data._data['trial_duration'][key] + 1
			if nduration > max_duration:
				max_duration = nduration

	### Update ex
	ex = existance[(sub_problem,time)]
	
	####################################################################		
	### 						Generate Model
	####################################################################
	import Core.Solvers.KDA.concrete_knapsackmodel as concrete_knapsackmodel
	if  'penalty' in _opts:
		Claimed_Resources = {}
		Current_Resources = {}
		for r in resources:
			Claimed_Resources[r] = 0
			Current_Resources[r] = w_max[r]
			
		model = concrete_knapsackmodel.Create_PenaltyKS_Max(items,resources,v,w,w_max,ex,max_duration, Claimed_Resources, Current_Resources,penval)
	else:
		model = concrete_knapsackmodel.create_knapsackmodel(items, resources,v,w,w_max,ex,mu,max_duration)	
	
	
	return model

def PRDP_Min_Solve_Model_Generator(knapsack_data, model_data, active_item_list, existance, sub_problem, time, max_duration, _opts, penval):
	####################################################################
	### 					Define Parameters
	####################################################################
	v = {}
	w = {}
	w_max = {}
	mu = {}
		
	## Set known parameters that are consistant for all instances
	items = knapsack_data.ItemList

	## Set the values for resource type
	resources = model_data._data['resource_type'][None]

	## Set the weight of each item. This should be the trial resource requirements
	for index in knapsack_data.ItemList:	
		w.update(knapsack_data.item_set[index]['item_weight'])
	
	## Set the maximum number of resources available of each type
	for index in model_data._data['resource_type'][None]:
		w_max[index] = model_data._data['max_resource'][(index,)]

	## Set mu. Mu is the amount of each resource remaining to complete all trials
	if 'probabilistic' in _opts:
		for index in knapsack_data.ItemList:
			mu.update(knapsack_data.item_set[index]['probmu'])
	else:	
		for index in knapsack_data.ItemList:
			mu.update(knapsack_data.item_set[index]['mu'])
	
	### Set Time Specific Value for all items
	for index in knapsack_data.ItemList:
				
		### Determine product
		product = model_data._data['product'][None][knapsack_data.items[index][0]]
				
		### Get the undepreciated value
		undepreciated_value = knapsack_data.item_set[index]['item_value']
				
		### set the time remaining
		time_remaining = knapsack_data.item_set[index]['remaining_time']
				
		### Set the probability of passing
		probability = knapsack_data.item_set[index]['probability']
				
		### Depreciate the undepreciated value
		depreciated_value = probability *(undepreciated_value - model_data._data['gammaL'][(product,)] * ( time + 1 + time_remaining))
				
		### Set the value
		v[index] = depreciated_value	
				
		### Determine Max Duration Parameter
			
		if existance[(sub_problem,time)][index] == 1:
					
			### Get item coords
			product = model_data._data['product'][None][knapsack_data.items[index][0]]
			trial = model_data._data['trial'][None][knapsack_data.items[index][1]]
					
			### Get item key	
			key = (product,trial)
					
			### Calculate the duration needed to finish
			nduration = time_remaining + model_data._data['trial_duration'][key] + 1
			if nduration > max_duration:
				max_duration = nduration
	
	####################################################################	
	### 				Fix Resource reservations 
	####################################################################
	Claimed_Resources = {}
	if len(active_item_list) == 0:
		for r in resources:
			Claimed_Resources[r] = 0
	else:
		for r in resources:
			Claimed_Resources[r] = 0
			for active_items in active_item_list:
				for trials in model_data._data['trial'][None]:
					if model_data._data['trial'][None].index(trials) == active_items.COORDS[1]:
						Claimed_Resources[r] += (active_items.isfinished - time) * model_data._data['resource_requirement'][(model_data._data['product'][None][active_items.COORDS[0]],model_data._data['trial'][None][active_items.COORDS[1]],r)]
					elif model_data._data['trial'][None].index(trials) > active_items.COORDS[1]:
						Claimed_Resources[r] += model_data._data['trial_duration'][(model_data._data['product'][None][active_items.COORDS[0]],model_data._data['trial'][None][active_items.COORDS[1]])]* model_data._data['resource_requirement'][(model_data._data['product'][None][active_items.COORDS[0]],model_data._data['trial'][None][active_items.COORDS[1]],r)]
				
	####################################################################		
	### 			Fix Current Resources Available
	####################################################################
	
	Current_Resources = {}
	resources_used = {}
	if len(active_item_list) == 0:
		for r in resources:
			resources_used[r] = 0
	else:
		for r in resources:
			resources_used[r] = 0
				
			for active_items in active_item_list:
				resources_used[r] += w[(active_items.ITEM_NAME,r)]
			
	for r in resources:
		Current_Resources[r] = w_max[r] - resources_used[r]
			
	### Update ex
	ex = existance[(sub_problem,time)]	
	
	####################################################################		
	### 						Generate Model
	####################################################################
	import Core.Solvers.KDA.concrete_knapsackmodel as concrete_knapsackmodel
	if  'penalty' in _opts:
		model = concrete_knapsackmodel.Create_PenaltyKS_Max(items,resources,v,w,w_max,ex,max_duration, Claimed_Resources, Current_Resources,penval)
	else:
		model = concrete_knapsackmodel.Create_IntKS(items,resources,v,w,w_max,ex,mu,max_duration, Claimed_Resources, Current_Resources)	
	return model

def PRDP_Min_Solve_Model_Generator_Greedy(knapsack_data, model_data, active_item_list, existance, sub_problem, time, max_duration, _opts, penval):
	####################################################################
	### 					Define Parameters
	####################################################################
	v = {}
	w = {}
	w_max = {}
		
	## Set known parameters that are consistant for all instances
	items = knapsack_data.ItemList

	## Set the values for resource type
	resources = model_data._data['resource_type'][None]

	## Set the weight of each item. This should be the trial resource requirements
	for index in knapsack_data.ItemList:	
		w.update(knapsack_data.item_set[index]['item_weight'])
	
	## Set the maximum number of resources available of each type
	for index in model_data._data['resource_type'][None]:
		w_max[index] = model_data._data['max_resource'][(index,)]

	
	### Set Time Specific Value for all items
	for index in knapsack_data.ItemList:
				
		### Determine product
		product = model_data._data['product'][None][knapsack_data.items[index][0]]
				
		### Get the undepreciated value
		undepreciated_value = knapsack_data.item_set[index]['item_value']
				
		### set the time remaining
		time_remaining = knapsack_data.item_set[index]['remaining_time']
				
		### Set the probability of passing
		probability = knapsack_data.item_set[index]['probability']
				
		### Depreciate the undepreciated value
		depreciated_value = probability *(undepreciated_value - model_data._data['gammaL'][(product,)] * ( time + 1 + time_remaining))
				
		### Set the value
		v[index] = depreciated_value	
				
		### Determine Max Duration Parameter
			
		if existance[(sub_problem,time)][index] == 1:
					
			### Get item coords
			product = model_data._data['product'][None][knapsack_data.items[index][0]]
			trial = model_data._data['trial'][None][knapsack_data.items[index][1]]
					
			### Get item key	
			key = (product,trial)
					
			### Calculate the duration needed to finish
			nduration = time_remaining + model_data._data['trial_duration'][key] + 1
			if nduration > max_duration:
				max_duration = nduration
	
	####################################################################	
	### 				Fix Resource reservations 
	####################################################################
	Claimed_Resources = {}
	if len(active_item_list) == 0:
		for r in resources:
			Claimed_Resources[r] = 0
	else:
		for r in resources:
			Claimed_Resources[r] = 0
			for active_items in active_item_list:
				for trials in model_data._data['trial'][None]:
					if model_data._data['trial'][None].index(trials) == active_items.COORDS[1]:
						Claimed_Resources[r] += (active_items.isfinished - time) * model_data._data['resource_requirement'][(model_data._data['product'][None][active_items.COORDS[0]],model_data._data['trial'][None][active_items.COORDS[1]],r)]
					elif model_data._data['trial'][None].index(trials) > active_items.COORDS[1]:
						Claimed_Resources[r] += model_data._data['trial_duration'][(model_data._data['product'][None][active_items.COORDS[0]],model_data._data['trial'][None][active_items.COORDS[1]])]* model_data._data['resource_requirement'][(model_data._data['product'][None][active_items.COORDS[0]],model_data._data['trial'][None][active_items.COORDS[1]],r)]
				
	####################################################################		
	### 			Fix Current Resources Available
	####################################################################
	
	Current_Resources = {}
	resources_used = {}
	if len(active_item_list) == 0:
		for r in resources:
			resources_used[r] = 0
	else:
		for r in resources:
			resources_used[r] = 0
				
			for active_items in active_item_list:
				resources_used[r] += w[(active_items.ITEM_NAME,r)]
			
	for r in resources:
		Current_Resources[r] = w_max[r] - resources_used[r]
			
	### Update ex
	ex = existance[(sub_problem,time)]	
	
	####################################################################		
	### 						Generate Model
	####################################################################
	import Core.Solvers.KDA.concrete_knapsackmodel as concrete_knapsackmodel
	model = concrete_knapsackmodel.Create_GreedyKS(items,resources,v,w,w_max,ex,max_duration, Claimed_Resources, Current_Resources)	
	return model
			
def results_processing(knapsack_data, model_data,i,time):
	### Find corresponding product/trial number
	Item_Coords = knapsack_data.items[i]
				
	### Get the name of the product and the trial
	product = model_data._data['product'][None][Item_Coords[0]]
	trial = model_data._data['trial'][None][Item_Coords[1]]
				
	### Using trial/product names get the duration of the item
	Item_Duration = model_data._data['trial_duration'][(product,trial)]
				
	### Create the new object
	from Core.Solvers.KDA.knapsack_item import Item_Selection 
	temp_object = Item_Selection(time,i,Item_Coords,Item_Duration)

	return_object1 = (product,trial,time)
	
	return return_object1, temp_object

def min_solve_sp_generation(item_monitor,time,i):
	finished_items = []
	for j in item_monitor[time-1][i]:
		if j.isfinished == time:
			### if items are finished increment the finished item count
			finished_items.append(j.COORDS)
								
	if len(finished_items) > 0:		
		generate_subproblems = True
	else:
		generate_subproblems = False
	
	return generate_subproblems, finished_items

def max_solve_sp_generation(item_monitor, time,i):
	#### Only need to generate subproblems after all items are finished
	finished_items = []
	for j in item_monitor[time-1][i]:
		if j.isfinished <= time:
			### if items are finished increment the finished item count
			finished_items.append(j.COORDS)
								
	if len(finished_items) == len(item_monitor[time-1][i]) and len(item_monitor[time-1][i]) != 0:		
		generate_subproblems = True
	else:
		generate_subproblems = False
		
	return generate_subproblems, finished_items

def every_solve_sp_generation(item_monitor, time,i):
	finished_items = []
	for j in item_monitor[time-1][i]:
		if j.isfinished == time:
			### if items are finished increment the finished item count
			finished_items.append(j.COORDS)
								
	if len(finished_items) > 0:
		generate_subproblems = True
	else:
		generate_subproblems = False
		
	return generate_subproblems, finished_items

def PRDP_SubProblem_Generation(finished_items, i, time, item_monitor,sp_solve,sp_realizations):
	import itertools
	
	### number of subproblems
	sp_count = 2 ** len(finished_items)
					 
	### outcomes of subproblems
	sp_outcome = itertools.product(range(2), repeat = len(finished_items))
					 
	### convert to useable format
	sp_outcome = tuple(sp_outcome)
			
	### Initialize iterator					
	s = 0
	while s < sp_count:
		
		### Name the subproblem
		sp_name = str(i) + "." + str(s)
								
		sp_solve[sp_name] = time 
		temp_realization = {}
		
		### Initialize iterator						
		k = 0
		while k < len(finished_items):
									
			temp_realization[finished_items[k]] = sp_outcome[s][k]
			k += 1
									
		### Assign Outcomes
		sp_realizations[sp_name] = dict(temp_realization)
						 
		### Readd the items that are not finished
		temp_object = ()
								
		for k in item_monitor[time-1][i]:
			if k.isfinished > time:
				temp_object += (k,)
							
		item_monitor[time][sp_name] = temp_object
							
		### increment s
		s += 1
	return sp_realizations, sp_solve, item_monitor

def non_initial_existance_vector(i, time, model_data, existance, knapsack_data, item_monitor, _opts, sp_realizations, results_storage):
	try: 
		### problem existed last time
		existance[(i,time-1)]
		n = i
	except:
	### there was a realization and the parent problem is given
		pp_name = i
		pp_name = pp_name.rsplit(".",1)	
		n = pp_name[0]
					
	### Create new existance vector
	existance[(i,time)] = {}
						
	### for each of the possible items calculate the eligibility to be in the knapsack
	for k in existance[(n,time-1)]:			
							
		### Was the item ineligible last time?
		if existance[(n,time-1)][k] == 0:
								
			###What was the previous trial?
			previous_trial = knapsack_data.items[k][1] - 1
								
			### What item cooresponds to the previous trial?
			new_coords = (knapsack_data.items[k][0], previous_trial)
						
			for kk in knapsack_data.ItemList:
				if knapsack_data.items[kk] == new_coords:
										
					### Did the item identified finish?
					for kkk in item_monitor[time-1][n]:
						if kkk.isfinished == time and kkk.ITEM_NAME == kk or kkk.isfinished <= time and kkk.ITEM_NAME == kk and 'max_solve' in _opts:
								### Is the option to wait until all items are complete?
								if 'max_solve' in _opts and time > 0:
									### Are there still items in the knapsack?
									if len(item_monitor[time][i]):
										existance[(i,time)][k] = 0
									else:
										if sp_realizations[i][new_coords] == 1:
											existance[(i,time)][k] = 1
										else:
											existance[(i,time)][k] = 0
												
								### Did the previous item pass?
								else:
									if sp_realizations[i][new_coords] == 1:
										existance[(i,time)][k] = 1
									else:
										existance[(i,time)][k] = 0
																
							
			### If the item corresponding to the previous trial did not finish then you can't pack the item
			try:
				existance[(i,time)][k]
			except:
				existance[(i,time)][k] = 0
						
		else:
							
			### If the item was eligible was it started last time?
			try:
				for b in results_storage[time-1][n]:
								
					prod = model_data._data['product'][None].index(b[0])
					trial = model_data._data['trial'][None].index(b[1])
					if (prod,trial) == knapsack_data.items[k]: 
						existance[(i,time)][k] = 0
							
				### If the item was not started it can still be packed
				try:
					existance[(i,time)][k]
				except:
					existance[(i,time)][k] = 1
			except:
				try:
					existance[(i,time)][k]
				except:
					existance[(i,time)][k] = 1
	return existance
	
def do_solve_calc(i,time,existance):
	do_solve = 0
					
	for k in existance[(i,time)]:
		do_solve += existance[(i,time)][k]
	return do_solve

def fixed_item_generator(i,time,sp_realizations, knapsack_data, model_data, fixed_parameters):
	added_fixed_items = []
	realization_list = []
	
	### Gather all realizations for this subproblem thus far
	sp = i
	req_realizations = []
	while sp != '0':
		
		for rls in sp_realizations[sp]:
			added_real = (model_data._data['product'][None][rls[0]], model_data._data['trial'][None][rls[1]],sp_realizations[sp][rls])
			req_realizations.append(added_real)
		sp_hold = sp.split('.')
		sp_new_list = sp_hold[:-1]
		sp = str('.'.join([x for x in sp_new_list]))

			
	### Compare the Required Realizations to the Fixed Parameter Realizations
	for (i,j,t,dec) in fixed_parameters:
		
		if t == time:
			
			### Determine if the set of required realizations matches the realizations of the sub-problems
			try:
				for jtms in fixed_parameters[(i,j,t,dec)]:
					if set(jtms) == set(req_realizations):

						### Loop over all items
						for items in knapsack_data.ItemList:
				
							### Get the corresponding coordinates for the drug,trial pair
							item_coords = (model_data._data['product'][None].index(i), model_data._data['trial'][None].index(j))
				
							### Add matching items to the list fixed items
							if item_coords == knapsack_data.items[items]:
								added_fixed_items.append((items,dec))
			except:
				pdb.set_trace()
	
	return 	added_fixed_items		
		
				
	

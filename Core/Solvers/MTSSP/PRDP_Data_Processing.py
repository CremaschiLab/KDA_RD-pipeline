import os
import sys
import pdb
import itertools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))
import MSSP.scenario_class as scenario_class 

class MTSSP_PRDP_Data_Processing:
	
	def __init__(self, model_data):
		## List of parameters to fix
		## Time independent
		self.product = []
		self.stage_gate = []
		self.time_step = []
		self.resource_type = []
	
		self.resource_max = {}
		self.gammaL = {}
		self.gammaD = {}
		self.duration = {}
		self.trial_cost = {}
		self.resource_required = {}
		self.revenue_max = {}
		self.success = {}
		self.running_revenue = {}
		self.open_revenue = {}
		self.discounting_factor ={}
		
		
		self.Scenario_Generation(model_data)

		##Set product
		self.product = model_data['product'][None]
	
		##Set stage_gate
		self.stage_gate = model_data['trial'][None]

		## Set time step
		self.time_step = model_data['time_step'][None]

		##Set resource type
		self.resource_type = model_data['resource_type'][None]
	
		## Set resource_max
		for items in model_data['max_resource']:
			self.resource_max[items[0]] = model_data['max_resource'][items]

		## Set GammaL
		for items in model_data['gammaL']:
			self.gammaL[items[0]] = model_data['gammaL'][items]

		## Set GammaD
		for items in model_data['gammaD']:
			self.gammaD[items[0]] = model_data['gammaD'][items]	
		
		## Set duration
		self.duration = model_data['trial_duration']

		## Set trial cost
		self.trial_cost = model_data['trial_cost']

		## Set resources required
		self.resource_required = model_data['resource_requirement']

		## Set revenue_max
		for items in model_data['maximum_revenue']:
			self.revenue_max[items[0]] = model_data['maximum_revenue'][items]
	
		## Set Last Time Step
		self.Last_Time_Step = len(self.time_step)

		## Set Last Trial
		self.last_trial = len(self.stage_gate)

		##Calculate Success matrix
		self.success = self.calc_success(self.product, len(self.stage_gate), self.List_of_Scenarios)

		## Calculate running rev
		self.running_revenue = self.calc_rr(self.revenue_max,self.gammaL,self.duration, self.product, self.stage_gate, self.time_step)
	
		##Calculate open rev
		self.open_revenue = self.calc_openrev(self.revenue_max,self.gammaL,self.duration, self.product, self.stage_gate, self.time_step, self.Last_Time_Step)

		##Calculate Discounting Factor
		self.discounting_factor = self.calc_discounting_factor(self.revenue_max,self.gammaL,self.trial_cost, self.product, self.stage_gate, self.Last_Time_Step)
	
		


	def calc_success(self,product, num_trial, List_of_Scenarios):
		## Generates a matrix based on the success of each product in each scenario
		success = {}
		try:
			len(List_of_Scenarios)		
			for scenario in List_of_Scenarios:
				oc = 0
				while oc < len(List_of_Scenarios[scenario].outcome):
					coords = (product[oc], scenario)
					if List_of_Scenarios[scenario].outcome[oc] == num_trial:
						success[coords] = 1
					else:
						success[coords] = 0
					oc += 1
		except:
			oc = 0
			while oc < len(List_of_Scenarios.outcome):
				coords = (product[oc])
				if List_of_Scenarios.outcome[oc] == num_trial:
					success[coords] = 1
				else:
					success[coords] = 0
				oc += 1
	

		return success

	def calc_rr(self,revenue_max,gammaL,duration, product, trial, time_step):
		##Calculates the Running Revenue according to the formulation given by Colvin
		rr = {}
		for i in product:
			for j in trial:
				for t in time_step:
					rr[(i,j,t)] = revenue_max[i] - gammaL[i] * ( t + sum(duration[(i,k)] for k in trial if k >= j))
				
		return rr 

	def calc_openrev(self,revenue_max,gammaL,duration, product, stage_gate, time_step, Last_Time_Step):
		##Calculates the Open Revenue according to the formulation given by Colvin
		opnrev = {}
		for i in product:
			for j in stage_gate:
				opnrev[(i,j)] = revenue_max[i] - gammaL[i] * ( Last_Time_Step + sum(duration[(i,k)] for k in stage_gate if k >= j))
				
		return opnrev 

	def calc_discounting_factor(self,revenue_max,gammaL,trial_cost, product, stage_gate, Last_Time_Step):
		##Calculates the discounting factor according to the formulation given by Colvin
		fij = {}
		for i in product:
			for j in stage_gate:
				top = .9 * revenue_max[i] - gammaL[i]* Last_Time_Step - sum(trial_cost[(i,k)] for k in stage_gate if k >= j) 
				bottom = (revenue_max[i] - gammaL[i] * Last_Time_Step)
				fij[(i,j)] = top/bottom
		return fij


	def Scenario_Generation(self,model_data):
		
		### Determine the set size of the independent variables (products, trials, and time steps)
		num_product = len(model_data['product'][None])
		num_trial = len(model_data['trial'][None])
		num_ts = len(model_data['time_step'][None])

		### Generate Outcomes
		self.Outcomes = itertools.product(range(num_trial + 1), repeat = num_product)
		self.Outcomes = tuple(self.Outcomes)
		
		### Generate Empty Variables
		self.List_of_Scenarios = {}
		self.SS=[]
		
		
		prod = model_data['product'][None]
		sg = model_data['trial'][None]
		prob = model_data['probability']
		
		### Initialize Scenario Counter
		scenario = 1
		
		### Name and generate Scenario Objects
		for items in self.Outcomes:
			scenario_name = scenario
			self.List_of_Scenarios[scenario_name] = scenario_class.scenario(items,prob,prod,sg)
			self.SS.append(scenario_name)
			scenario += 1

def PRDP_Realization(s,ts,model_data, results):
	
	### Generate new empty Scenario Set
	intermediate = []
	
	scenario_set = []
	
	
	#######################################
	### Define Parameters from model_data
	#######################################
	
	### List of products
	prod = model_data.Product
	
	### List of stages
	sg = model_data.Stage_Gate
	
	### List of the duration of each trial
	duration = model_data.Duration
	
	### For all combinations of drug/trial pairs
	for i in prod:
		for j in sg:
			
			### If the trial could have been started in the planning horizon
			if ts-duration[(i,j)] >= 0:
				
				### When would it have started
				previous = ts-duration[(i,j)] 
				
				### Define the indicies of the drug trial pair
				index = prod.index(i)
				jndex = sg.index(j)
				
				
				#Check to see if the trial was started at that point
				try:
					### Check to see if scenario set has scenarios in it
					s[0]
					
					### If the trial was started 
					if Scenario_Results[s[0]][index][jndex][previous] == 1:
						
						### If the new set is empty 
						if intermediate == []:
							
							### Create New Outcome Sets
							p = []
							f = []
							
							### For all scenarios in the scenario set
							for items in s:
								
								### If the trial is successful add to pass set
								if model_data.List_of_Scenarios[items].outcome[index] > jndex:
									p.append(items)
									
								### Otherwise add to fail set	
								else:
									f.append(items)
									
								### Add subsets to the New Set	
								intermediate.append(p)
								intermediate.append(f)
						else:
							### Duplicate the Intermediate Variable		
							intermediate2 = list(intermediate)
							
							### See which Items need to be replaced
							for items in intermediate2:
								
								### Generate New Outcome Sets
								p = []
								f = []
								
								### Determine the index of the scenario set
								itemtoreplace = intermediate.index(items)
								
								### Sort scenarios based on outcome
								for k in items:
									if model_data.List_of_Scenarios[k].outcome[index] > jndex:
										p.append(k)
									else:
										f.append(k)
									intermediate[itemtoreplace] = p
									intermediate.append(f)				
				except:
					pass
					
				#Set the Scenario Subsets
				if intermediate == []:
					scenario_set.append(s)
				else:
					scenario_set += intermediate
					
	return scenario_set			
					
def results_matrix_generator(mtssp_data):
	## Generate Results Lists
	Scenario_Results = {}
	
	for items in mtssp_data.SS:
		ibox = []
		for i in mtssp_data.Product:
			jbox = []
			for j in mtssp_data.Stage_gate:
				tbox = [0] * num_ts
				jbox.append(tbox) 
			ibox.append(jbox)
		Scenario_Results[items] = ibox
	return Scenario_Results	

def resource_utilization(ts,mtssp_data,Scenario_Results,scenarios):
	
	### determine the number of scenarios in the current set
	if len(scenarios) <= 1:
		
		### If the length is less than or equal to one then we have a realization
		pass
		
	else:
		### Get a scenario
		sis = scenarios[0]
		
		### Count the resource utilization
		resource_count = {}
		
		for r in mtssp_data.resource_type:
			resource_count[r] = 0

		for i in mtssp_data.Product:
			for j in mtssp_data.Stage_Gate:
				index = mtssp_data.Product.index(i)
				jndex = mtssp_data.Stage_Gate.index(j)
				tpr = 0
				while tpr < ts:
					if Scenario_Results[sis][index][jndex][tpr] == 1:
						if tpr > ts - mtssp_data.duration[(i,j)]:
							for r in mtssp_data.resource_type:
								resource_count[r] += mtssp_data.resource_required[(i,j,r)]
					tpr += 1
					
	return resource_count				

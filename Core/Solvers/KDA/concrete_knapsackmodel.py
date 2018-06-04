#
# This is the knapsack general problem
#
import sys
import os
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(dirname(dirname(abspath(__file__))))))
from pyomo.environ import *
from pyomo.opt import SolverFactory

#Information for the problem

def create_knapsackmodel(items,resources,v,w,w_max,ex,mu,ts):

	#Model Formulation
	model = ConcreteModel()

	model.items = items
	model.resources = resources

	model.v = v
	model.w = w
	model.w_max = w_max
	model.x = Var(model.items, within=Binary)

	model.ex = ex
	model.mu = mu
	model.ts = ts

	def existance_rule(model,i):
		if model.ex[i] == 0:
			return model.x[i] == 0
		else: 
			return Constraint.Skip
	model.existance = Constraint(model.items, rule=existance_rule)
		
	def value_rule(model):
		return sum(model.v[i] * model.x[i] * model.ex[i] for i in model.items)
	model.value = Objective(rule=value_rule, sense=maximize)

	def weight_rule(model,j):
		return sum(model.w[i,j] * model.x[i] for i in model.items) <= model.w_max[j]
	model.weight = Constraint(model.resources, rule=weight_rule)

	def flow_rule(model,j):
		return sum(model.mu[i,j] * model.x[i] for i in model.items) <= model.ts * model.w_max[j]
	model.flow = Constraint(model.resources, rule=flow_rule)

	return model
	
def Create_IntKS(items,resources,v,w,w_max,ex,mu,ts, claimedresources, currentresources):

	#Model Formulation
	model = ConcreteModel()

	model.ITEMS = items
	model.RESOURCES = resources

	model.claimedresources = claimedresources
	model.currentresources = currentresources
	model.v = v
	model.w = w
	model.w_max = w_max
	model.x = Var(model.ITEMS, within=Binary)
	

	model.ex = ex
	model.mu = mu
	model.ts = ts

	def existance_rule(model,i):
		if model.ex[i] == 0:
			return model.x[i] == 0
		else: 
			return Constraint.Skip
	model.existance = Constraint(model.ITEMS, rule=existance_rule)
		
	def value_rule(model):
		return sum(model.v[i] * model.x[i] * model.ex[i] for i in model.ITEMS)
	model.value = Objective(rule=value_rule, sense=maximize)

	def weight_rule(model,j):
		return sum(model.w[i,j] * model.x[i] for i in model.ITEMS) <= model.currentresources[j]
	model.weight = Constraint(model.RESOURCES, rule=weight_rule)

	def flow_rule(model,j):
		return sum(model.mu[i,j] * model.x[i] for i in model.ITEMS) <= model.ts * model.w_max[j] - model.claimedresources[j]
	model.flow = Constraint(model.RESOURCES, rule=flow_rule)

	return model
	
def Create_GreedyKS(items,resources,v,w,w_max,ex,ts, claimedresources, currentresources):

	#Model Formulation
	model = ConcreteModel()

	model.ITEMS = items
	model.RESOURCES = resources

	model.claimedresources = claimedresources
	model.currentresources = currentresources
	model.v = v
	model.w = w
	model.w_max = w_max
	model.x = Var(model.ITEMS, within=Binary)
	

	model.ex = ex
	model.ts = ts

	def existance_rule(model,i):
		if model.ex[i] == 0:
			return model.x[i] == 0
		else: 
			return Constraint.Skip
	model.existance = Constraint(model.ITEMS, rule=existance_rule)
		
	def value_rule(model):
		return sum(model.v[i] * model.x[i] * model.ex[i] for i in model.ITEMS)
	model.value = Objective(rule=value_rule, sense=maximize)

	def weight_rule(model,j):
		return sum(model.w[i,j] * model.x[i] for i in model.ITEMS) <= model.currentresources[j]
	model.weight = Constraint(model.RESOURCES, rule=weight_rule)

	return model

"""	
def Create_PenaltyKS_Max(items,resources,v,w,w_max,ex,ts, claimedresources, currentresources,penalty_rate):
	model = ConcreteModel()
	
	model.ITEMS = items
	model.RESOURCES = resources

	model.claimedresources = claimedresources
	model.currentresources = currentresources
	model.v = v
	model.w = w
	model.w_max = w_max
	model.Penalty_Rate = penalty_rate
	model.x = Var(model.ITEMS, within=Binary)
	model.y = Var(within = Binary)
	model.Penalty = Var(within = NonNegativeReals)	
	model.BTX = Var()

	model.ex = ex
	model.ts = ts
	model.M = 100
	model.M1 = 100
	model.M2 = 100

	def existance_rule(model,i):
		if model.ex[i] == 0:
			return model.x[i] == 0
		else: 
			return Constraint.Skip
	model.existance = Constraint(model.ITEMS)
		
	def value_rule(model):
		return sum(model.v[i] * model.x[i] * model.ex[i] for i in model.ITEMS) - model.Penalty
	model.value = Objective(rule=value_rule, sense=maximize)
	
	def penalty_existance_rule(model,j):
		return sum(model.w[i,j] * model.x[i] for i in model.ITEMS) - (model.ts * model.w_max[j] - model.claimedresources[j]) + model.M * model.y  >= 0
	model.penalty_existance = Constraint(model.RESOURCES, rule= penalty_existance_rule)
	
	def penalty_bound_rule(model):
		return model.Penalty <= model.M1*(1-model.y)
	model.penalty_bound = Constraint(rule=penalty_bound_rule)
	
	
	def overage_calc_rule(model):
		return model.BTX == model.Penalty_Rate * sum(sum(model.w[i,j] * model.x[i] for i in model.ITEMS)- (model.ts * model.w_max[j] - model.claimedresources[j]) for j in model.RESOURCES)
	model.overage_calc = Constraint(rule=overage_calc_rule)
	
	def penalty_value_rule(model):
		return	-model.Penalty + model.BTX <= model.M2 * (model.y)
	model.penalty_value = Constraint(rule = penalty_value_rule)
		
	def weight_rule(model,j):
		return sum(model.w[i,j] * model.x[i] for i in model.ITEMS) <= model.currentresources[j]
	model.weight = Constraint(model.RESOURCES, rule=weight_rule)


	return model
"""
def Create_PenaltyKS_Max(items,resources,v,w,w_max,ex,ts, claimedresources, currentresources,penalty_rate):
	model = ConcreteModel()
	
	model.ITEMS = items
	model.RESOURCES = resources

	model.claimedresources = claimedresources
	model.currentresources = currentresources
	model.v = v
	model.w = w
	model.w_max = w_max
	model.Penalty_Rate = penalty_rate
	model.x = Var(model.ITEMS, within=Binary)
	model.y = Var(model.RESOURCES, within = Binary)
	model.z = Var(model.ITEMS, model.RESOURCES, within=Binary)
	model.Penalty = Var(within = NonNegativeReals)	
	

	model.ex = ex
	model.ts = ts
	model.M = 100

	def existance_rule(model,i):
		if model.ex[i] == 0:
			return model.x[i] == 0
		else: 
			return Constraint.Skip
	model.existance = Constraint(model.ITEMS,rule=existance_rule)
		
	def value_rule(model):
		return sum(model.v[i] * model.x[i] * model.ex[i] for i in model.ITEMS) - sum((model.Penalty_Rate * sum(model.w[i,r]*model.z[i,r] for i in model.ITEMS) - model.Penalty_Rate * (model.ts * model.w_max[r] - model.claimedresources[r])*model.y[r]) for r in model.RESOURCES)
	model.value = Objective(rule=value_rule, sense=maximize)
	
	def objective_linearization_rule(model,i,r):
		return model.z[i,r] <= model.x[i]
	model.objective_linearization = Constraint( model.ITEMS, model.RESOURCES,rule=objective_linearization_rule)
	
	def objective_linearization2_rule(model,i,r):
		return model.z[i,r] <= model.y[r]
	model.objective_linearization2 = Constraint(model.ITEMS, model.RESOURCES,rule=objective_linearization2_rule)
	
	def objective_linearization3_rule(model,i,r):
		return model.z[i,r] >= model.x[i] + model.y[r] - 1
	model.objective_linearization3 = Constraint(model.ITEMS, model.RESOURCES,rule=objective_linearization3_rule)
	
	def BigM_rule(model,r):
		return sum(model.w[i,r]*model.x[i] for i in model.ITEMS) - (model.ts*model.w_max[r] - model.claimedresources[r]) <= model.M * model.y[r]
	model.BigM = Constraint(model.RESOURCES,rule=BigM_rule)
	
	def BigM2_rule(model,r):
		return sum(model.w[i,r]*model.x[i] for i in model.ITEMS) - (model.ts*model.w_max[r] - model.claimedresources[r]) >= 1 - model.M * (1-model.y[r])
	model.BigM2 = Constraint(model.RESOURCES,rule=BigM2_rule)
		
	def weight_rule(model,j):
		return sum(model.w[i,j] * model.x[i] for i in model.ITEMS) <= model.currentresources[j]
	model.weight = Constraint(model.RESOURCES, rule=weight_rule)
	return model
		
def Create_ProbKS(items,resources,v,w,w_max,ex,mu,ts, claimedresources, currentresources):
	model = ConcreteModel()
	
	
	model.ITEMS = items
	model.RESOURCES = resources

	model.claimedresources = claimedresources
	model.currentresources = currentresources
	model.v = v
	model.w = w
	model.w_max = w_max
	model.x = Var(model.ITEMS, within=Binary)

	model.ex = ex
	model.mu = mu
	model.ts = ts

	def existance_rule(model,i):
		if model.ex[i] == 0:
			return model.x[i] == 0
		else: 
			return Constraint.Skip
	model.existance = Constraint(model.ITEMS, rule=existance_rule)
		
	def value_rule(model):
		return sum(model.v[i] * model.x[i] * model.ex[i] for i in model.ITEMS)
	model.value = Objective(rule=value_rule, sense=maximize)

	def weight_rule(model,j):
		return sum(model.w[i,j] * model.x[i] for i in model.ITEMS) <= model.currentresources[j]
	model.weight = Constraint(model.RESOURCES, rule=weight_rule)

	def flow_rule(model,j):
		return sum(model.mu[i,j] * model.x[i] for i in model.ITEMS) <= model.ts * model.w_max[j] - model.claimedresources[j]
	model.flow = Constraint(model.RESOURCES, rule=flow_rule)
	return model

def Create_PenaltyKS(items,resources,v,w,w_max,ex,ts, claimedresources, currentresources,penalty_rate):
	model = ConcreteModel()
	
	model.ITEMS = items
	model.RESOURCES = resources

	model.claimedresources = claimedresources
	model.currentresources = currentresources
	model.v = v
	model.w = w
	model.w_max = w_max
	model.Penalty_Rate = penalty_rate
	model.x = Var(model.ITEMS, within=Binary)
	model.y = Var(within = Binary)
	model.Penalty = Var(within = PositiveReals)
	

	model.ex = ex
	model.ts = ts
	model.M = 25
	model.M1 = 25
	model.M2 = 25

	def existance_rule(model,i):
		if model.ex[i] == 0:
			return model.x[i] == 0
		else: 
			return Constraint.Skip
	model.existance = Constraint(model.ITEMS, rule=existance_rule)
		
	def value_rule(model):
		return sum(model.v[i] * model.x[i] * model.ex[i] for i in model.ITEMS) - model.Penalty
	model.value = Objective(rule=value_rule, sense=maximize)
	
	def penalty_existance_rule(model,j):
		return sum(model.w[i,j] * model.x[i] for i in model.ITEMS)- (model.ts * model.w_max[j] - model.claimedresources[j]) + model.M1 * model.y  >= 0
	model.penalty_existance = Constraint(model.RESOURCES, rule= penalty_existance_rule)
	
	def penalty_bound_rule(model):
		return model.Penalty <= model.M1*(1-model.y)
	model.penalty_bound = Constraint(rule=penalty_bound_rule)
	
	def penalty_value_rule(model):
		return	-model.Penalty + model.Penalty_Rate * sum((sum(model.w[i,j] * model.x[i] for i in model.ITEMS)- (model.ts * model.w_max[j] - model.claimedresources[j]))for j in model.RESOURCES) >= model.M2 * (model.y)
	model.penalty_value = Constraint(rule = penalty_value_rule)
		
	def weight_rule(model,j):
		return sum(model.w[i,j] * model.x[i] for i in model.ITEMS) <= model.currentresources[j]
	model.weight = Constraint(model.RESOURCES, rule=weight_rule)


	return model

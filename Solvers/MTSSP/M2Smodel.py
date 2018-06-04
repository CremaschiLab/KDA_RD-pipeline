
import sys
import os
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(dirname(dirname(abspath(__file__))))))
from coopr.pyomo import *

def create_M2S_model(product,stage_gate,time_step,resource_type,scenario,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,success,last_trial,last_time_step,probability,current_time_step, scenario_in_set, running_revenue, open_revenue, discount_factor, previous_decision):
	model = ConcreteModel()

	##Parameters##
	##Independent parameters (Sets)
	model.PRODUCT = product
	model.STAGE_GATE = stage_gate
	model.TIME_STEP = time_step
	model.RESOURCE_TYPE = resource_type
	model.SCENARIO = scenario
	
	##Time independent parameters
	model.Resource_Max = resource_max
	model.GammaL = gammaL
	model.GammaD = gammaD
	model.Duration = duration
	model.Trial_Cost = trial_cost
	model.Resources_Required = resource_required
	model.Revenue_Max = revenue_max
	model.Success = success
	model.Last_Trial = last_trial

	##Time Dependent parameters
	model.LastTimeStep = last_time_step
	model.Probability = probability
	model.Current_Time_Step = current_time_step
	model.Scenario_In_Set = scenario_in_set


	###Variables###
	model.Decision_X = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)
	model.Decision_Y = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)
	model.Decision_Z = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)
	
	##Parameters for intermediate calculations
	model.Running_Revenue = running_revenue
	model.Open_Revenue = open_revenue
	model.Discount_Factor = discount_factor
	model.Previous_Decision= previous_decision
		
	model.Cst = Var(model.SCENARIO)
	model.FRv = Var(model.SCENARIO)
	model.FRv1 = Var(model.SCENARIO)
	model.FRv2 = Var(model.SCENARIO)
	model.Rv = Var(model.SCENARIO)
	

	##Objective##
	def ENPV(model):
		return sum(model.Probability[s] * (model.FRv[s] + model.Rv[s] - model.Cst[s]) for s in model.SCENARIO)
	model.Expected_NPV = Objective(rule=ENPV, sense=maximize)

	
	###Calculate Costs associated with each trial
	def Costs(model,s):
		return model.Cst[s] == sum((1 - 0.025 * (t - 1)) * model.Trial_Cost[i,j] * model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE for t in model.TIME_STEP )
	model.Total_Costs = Constraint(model.SCENARIO,rule=Costs)

	###Calculate the net revenue for each scenario
	def Net_Revenue_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv[s] == sum(model.Success[i,s]*((model.Revenue_Max[i] * model.Decision_X[i,last_trial,t,s]) - model.GammaD[i] * sum(model.Decision_Z[i,j,t,s] for j in model.STAGE_GATE if j > 1)- model.GammaL[i]*(t + model.Duration[i, last_trial] * model.Decision_X[i,last_trial,t,s])) for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue = Constraint(model.SCENARIO)

	###Calculate the free Revenue
	def Free_Rev_1_rule(model,s,m):
		last_time = model.LastTimeStep
		return model.FRv1[s] == sum(model.Success[i,s] * model.Open_Revenue[i,j] * model.Discount_Factor[i,j]* model.Decision_Z[i,j,last_time,s] for i in model.PRODUCT for j in model.STAGE_GATE)
	model.Free_Rev_1 = Constraint(model.SCENARIO, model.TIME_STEP, rule=Free_Rev_1_rule)

	def Free_Rev_2_rule(model,s):
		return model.FRv2[s] == sum(model.Success[i,s] * model.Running_Revenue[i,j,t] * model.Discount_Factor[i,j+1]*model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE if j < model.Last_Trial for t in model.TIME_STEP if t > model.LastTimeStep - model.Duration[i,j])
	model.Free_Rev_2 = Constraint(model.SCENARIO, rule=Free_Rev_2_rule)

	def Free_Revenue_rule(model,s):
		return model.FRv[s] == model.FRv1[s] + model.FRv2[s] 
	model.Free_Revenue = Constraint(model.SCENARIO)

	### Constraint-- The trial is complete if the trial was started a duration ago
	def Trial_Finish_rule(model,i,j,t,s):
		past_duration = t - model.Duration[i,j]
		if t-1 < 1 and past_duration < 1 :
			return model.Decision_Y[i,j,t,s] == 0
		elif  t-1 >= 1 and  past_duration < 1 :
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s]
		elif  t-1 < 1 and past_duration  >= 1 :
			return model.Decision_Y[i,j,t,s] == model.Decision_X[i,j,past_duration,s]
		else:
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s] + model.Decision_X[i,j,past_duration,s] 
	model.Trial_Finish = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO)

	### Constraint-- First time step starting rule
	def First_Time_Step_rule(model,i,s):
		return model.Decision_Z[i,1,1,s] == 1 - model.Decision_X[i,1,1,s] 
	model.First_Time_Step = Constraint(model.PRODUCT,model.SCENARIO)

	### Constraint--
	def Constraint_1_rule(model,i,t,s):
		if t > 1:
			return model.Decision_Z[i,1,t,s] == model.Decision_Z[i,1,t-1,s] - model.Decision_X[i,1,t,s]
		else:
			return Constraint.Skip
	model.Constraint_1 = Constraint(model.PRODUCT, model.TIME_STEP, model.SCENARIO)

	### Constraint--
	def Constraint_2_rule(model,i,j,t,s):
		if j > 1 and t-model.Duration[i,j-1] > 0 and t>1:	
			pd = t-model.Duration[i,j-1]
			previous_trial = j-1
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] + model.Decision_X[i,previous_trial,pd,s] - model.Decision_X[i,j,t,s]
		elif j>1 and t>1:
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] - model.Decision_X[i,j,t,s]
		elif t==1 and j>1:
			return model.Decision_Z[i,j,t,s] == 0
		else:
			return Constraint.Skip
	model.Constraint_2 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO) 

	### Constraint--You can only start each trial once
	def Constraint_3_rule(model,i,j,s):
 		return sum(model.Decision_X[i,j,t,s] for t in model.TIME_STEP) <= 1
	model.Constraint_3 = Constraint(model.PRODUCT,model.STAGE_GATE,model.SCENARIO)

	### Constraint--
	def Constraint_4_rule(model,i,j,t,s):
		if j > 1:
			previous_trial = j-1
			return sum(model.Decision_X[i,j,tprime,s] for tprime in model.TIME_STEP if tprime <= t) <= model.Decision_Y[i,previous_trial,t,s]
		else:
			return Constraint.Skip
	model.Constraint_4 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO)

	### Constraint-- Ensures resources are managed correctly
	def Resource_Constraint_rule(model,r,t,s):
		return sum(model.Resources_Required[i,j,r]*model.Decision_X[i,j,tprime,s] for i in model.PRODUCT for j in model.STAGE_GATE for tprime in model.TIME_STEP if tprime > (t - model.Duration[i,j]) and tprime <= t) <= model.Resource_Max[r]
	model.Resource_Constraint = Constraint(model.RESOURCE_TYPE, model.TIME_STEP, model.SCENARIO)

	### M2S Specific Constraints
	###Need Overscheduling prevention and constraint to force a pick in the current time step

	### Overscheduling constraint
	def OS_Constraint_rule(model,r,s):
		cts= model.Current_Time_Step
		return (model.LastTimeStep * model.Resource_Max[r]) >= sum(model.Duration[i,j]*model.Resources_Required[i,j,r]*model.Decision_X[i,jprime,cts,s] for j in model.STAGE_GATE for i in model.PRODUCT for jprime in model.STAGE_GATE if jprime >= j)
	model.OS_Constraint = Constraint(model.RESOURCE_TYPE, model.SCENARIO)

	def Decision_Required_rule(model,s):
		return 1 <= sum(model.Decision_X[i,j,model.Current_Time_Step,s] for i in model.PRODUCT for j in model.STAGE_GATE)
	model.Decision_Required = Constraint(model.SCENARIO)

	def NAC_Constraint_rule(model,i,j,s):
		return  model.Decision_X[i,j,model.Current_Time_Step,s] == model.Decision_X[i,j,model.Current_Time_Step, model.Scenario_In_Set]
	model.NAC_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE,model.SCENARIO)
	
	def FP_Constraint_rule(model,i,j,t,s):
		if model.Current_Time_Step > 1 and t < model.Current_Time_Step:
			if s in model.Previous_Decision[i,j,t]:
				return model.Decision_X[i,j,t,s] == 1	
			else:
				return Constraint.Skip	
		else:
			return Constraint.Skip
	model.FP_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO)
	
	
	return model 

	
	


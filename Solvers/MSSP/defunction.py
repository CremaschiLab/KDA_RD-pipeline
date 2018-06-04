import sys
import os
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(dirname(dirname(abspath(__file__))))))
from pyomo.environ import *
from pyomo.dae import *
import pdb

def de(prod,sg,time_step,resource_type,ss,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,probability, success,last_time_step, last_trial, rev_run, open_rev, discounting_factor, phi, phii, phij,outcome):

	model = ConcreteModel()

	##Parameters##
	model.PRODUCT = prod
	model.STAGE_GATE = sg
	model.TIME_STEP = time_step
	model.RESOURCE_TYPE = resource_type
	model.SCENARIO = ss

	model.Resource_Max = resource_max
	model.GammaL = gammaL
	model.GammaD = gammaD
	model.Duration = duration 
	model.Trial_Cost = trial_cost
	model.Resources_Required = resource_required

	model.Revenue_Max = revenue_max
	model.Probability = probability
	model.Success = success
	model.Outcome = outcome

	model.LastTimeStep = last_time_step
	model.Last_Trial = last_trial

	model.Running_Revenue = rev_run

	model.Open_Revenue=open_rev

	model.Discount_Factor= discounting_factor

	model.Phi= phi

	model.phii = phii

	model.phij =phij

	###Variables###
	model.Decision_X = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)
	model.Decision_Y = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)
	model.Decision_Z = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)



	model.Cst = Var(model.SCENARIO)
	model.FRv = Var(model.SCENARIO)
	model.FRv1 = Var(model.SCENARIO)
	model.FRv2 = Var(model.SCENARIO)
	model.Rv = Var(model.SCENARIO)
	model.Rv1 = Var(model.SCENARIO)
	model.Rv2 = Var(model.SCENARIO)
	model.Rv3 = Var(model.SCENARIO)


	def ENPV(model):
		return sum(model.Probability[s] * (model.FRv[s] + model.Rv[s] - model.Cst[s]) for s in model.SCENARIO)
	model.Expected_NPV = Objective(rule=ENPV, sense=maximize)

	
	###Calculate Costs associated with each trial
	def Costs(model,s):
		return model.Cst[s] == sum((1 - (0.025 * (t - 1))) * model.Trial_Cost[i,j] * model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE for t in model.TIME_STEP )
	model.Total_Costs = Constraint(model.SCENARIO,rule=Costs)

	###Calculate the net revenue for each scenario
	def Net_Revenue_rule(model,s):
		return model.Rv[s] == model.Rv1[s] + model.Rv2[s] + model.Rv3[s]
	model.Net_Revenue = Constraint(model.SCENARIO, rule=Net_Revenue_rule)

	def Net_Revenue1_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv1[s] == sum(model.Success[i,s]*(model.Revenue_Max[i] * model.Decision_X[i,last_trial,t,s]) for i in model.PRODUCT for t in model.TIME_STEP) 
	model.Net_Revenue1 = Constraint(model.SCENARIO, rule=Net_Revenue1_rule)

	def Net_Revenue2_rule(model,s):	
		return model.Rv2[s] == sum(-model.Success[i,s]*model.GammaD[i] * sum(model.Decision_Z[i,j,t,s] for j in model.STAGE_GATE if j > 1) for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue2 = Constraint(model.SCENARIO, rule=Net_Revenue2_rule)

	def Net_Revenue3_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv3[s] == sum(-model.Success[i,s]*model.GammaL[i]*(t + model.Duration[i, last_trial]) * model.Decision_X[i,last_trial,t,s] for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue3 = Constraint(model.SCENARIO, rule=Net_Revenue3_rule)

	###Calculate the free Revenue
	def Free_Rev_1_rule(model,s):
		last_time = model.LastTimeStep
		return model.FRv1[s] == sum(model.Success[i,s] * model.Open_Revenue[i,j] * model.Discount_Factor[i,j]* model.Decision_Z[i,j,last_time,s] for i in model.PRODUCT for j in model.STAGE_GATE)
	model.Free_Rev_1 = Constraint(model.SCENARIO, rule=Free_Rev_1_rule)

	def Free_Rev_2_rule(model,s):
		return model.FRv2[s] == sum(model.Success[i,s] * model.Running_Revenue[i,j,t] * model.Discount_Factor[i,j+1]*model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE if j < model.Last_Trial for t in model.TIME_STEP if t > model.LastTimeStep - model.Duration[i,j])
	model.Free_Rev_2 = Constraint(model.SCENARIO, rule=Free_Rev_2_rule)

	def Free_Revenue_rule(model,s):
		return model.FRv[s] == model.FRv1[s] + model.FRv2[s] 
	model.Free_Revenue = Constraint(model.SCENARIO, rule=Free_Revenue_rule)

	### Constraint-- The trial is complete if the trial was started a duration ago
	def Trial_Finish_rule(model,i,j,t,s):
		past_duration = t - model.Duration[i,j]
		if t==1:
			return model.Decision_Y[i,j,t,s] == 0
		elif  t > 1 and  past_duration < 1 :
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s]
		else:
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s] + model.Decision_X[i,j,past_duration,s] 
	model.Trial_Finish = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Trial_Finish_rule)

	### Constraint-- First time step starting rule
	def First_Time_Step_rule(model,i,s):
		return model.Decision_Z[i,1,1,s] == 1 - model.Decision_X[i,1,1,s] 
	model.First_Time_Step = Constraint(model.PRODUCT,model.SCENARIO, rule=First_Time_Step_rule)

	### Constraint--
	def Constraint_1_rule(model,i,t,s):
		if t > 1:
			return model.Decision_Z[i,1,t,s] == model.Decision_Z[i,1,t-1,s] - model.Decision_X[i,1,t,s]
		else:
			return Constraint.Skip
	model.Constraint_1 = Constraint(model.PRODUCT,model.TIME_STEP, model.SCENARIO, rule=Constraint_1_rule)

	### Constraint--
	def Constraint_2_rule(model,i,j,t,s):
		if j > 1 and t-model.Duration[i,j-1] > 0 and t>1:	
			pd = t-model.Duration[i,j-1]
			previous_trial = j-1
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] + model.Decision_X[i,previous_trial,pd,s] - model.Decision_X[i,j,t,s]
		elif j>1 and t>1:
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] - model.Decision_X[i,j,t,s]
		elif t==1 and j>1:
			return model.Decision_Z[i,j,t,s] == -model.Decision_X[i,j,t,s]
		else:
			return Constraint.Skip
	model.Constraint_2 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_2_rule) 

	### Constraint--You can only start each trial once
	def Constraint_3_rule(model,i,j,s):
 		return sum(model.Decision_X[i,j,t,s] for t in model.TIME_STEP) <= 1
	model.Constraint_3 = Constraint(model.PRODUCT,model.STAGE_GATE,model.SCENARIO,rule=Constraint_3_rule)

	### Constraint--
	def Constraint_4_rule(model,i,j,t,s):
		if j > 1:
			previous_trial = j-1
			return sum(model.Decision_X[i,j,tprime,s] for tprime in model.TIME_STEP if tprime <= t) <= model.Decision_Y[i,previous_trial,t,s]
		else:
			return Constraint.Skip
	model.Constraint_4 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_4_rule)

	### Constraint-- Ensures resources are managed correctly
	def Resource_Constraint_rule(model,r,t,s):
		return sum(model.Resources_Required[i,j,r]*model.Decision_X[i,j,tprime,s] for i in model.PRODUCT for j in model.STAGE_GATE for tprime in model.TIME_STEP if tprime > (t - model.Duration[i,j]) and tprime <= t) <= model.Resource_Max[r]
	model.Resource_Constraint = Constraint(model.RESOURCE_TYPE, model.TIME_STEP, model.SCENARIO,rule= Resource_Constraint_rule)

	##DE specific constriants

	def NAC_Constraint_rule(model,i,s):
		return  model.Decision_X[i,1,1,1] == model.Decision_X[i,1,1,s]
	model.NAC_Constraint = Constraint(model.PRODUCT, model.SCENARIO,rule=NAC_Constraint_rule)
	
	def NAC2_Constraint_rule(model,i,j,t,s,sprime):
		if t >1 and sprime > s:
			if (s,sprime) in model.Phi:
				iss = model.phii[s,sprime]
				jss = model.phij[s,sprime]
				return  -model.Decision_Y[iss,jss,t,s] <= model.Decision_X[i,j,t,s]-model.Decision_X[i,j,t,sprime]
			else:
				return Constraint.Skip
		else:
			return Constraint.Skip
	model.NAC2_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,model.SCENARIO,rule=NAC2_Constraint_rule)

	def NAC3_Constraint_rule(model,i,j,t,s,sprime):
		if t >1 and sprime > s:
			if (s,sprime) in model.Phi:
				iss = model.phii[s,sprime]
				jss = model.phij[s,sprime]
				return  model.Decision_Y[iss,jss,t,s] >= model.Decision_X[i,j,t,s]-model.Decision_X[i,j,t,sprime]
			else:
				return Constraint.Skip
		else:
			return Constraint.Skip
	model.NAC3_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, model.SCENARIO,rule=NAC3_Constraint_rule)

	return model
		
def deLR(prod,sg,time_step,resource_type,ss,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,probability, success,last_time_step, last_trial, rev_run, open_rev, discounting_factor, phi, phii, phij,outcome):

	model = ConcreteModel()

	##Parameters##
	model.PRODUCT = prod
	model.STAGE_GATE = sg
	model.TIME_STEP = time_step
	model.RESOURCE_TYPE = resource_type
	model.SCENARIO = ss

	model.Resource_Max = resource_max
	model.GammaL = gammaL
	model.GammaD = gammaD
	model.Duration = duration 
	model.Trial_Cost = trial_cost
	model.Resources_Required = resource_required

	model.Revenue_Max = revenue_max
	model.Probability = probability
	model.Success = success
	model.Outcome = outcome

	model.LastTimeStep = last_time_step
	model.Last_Trial = last_trial

	model.Running_Revenue = rev_run

	model.Open_Revenue=open_rev

	model.Discount_Factor= discounting_factor

	model.Phi= phi

	model.phii = phii

	model.phij =phij

	###Variables###
	model.Decision_X = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, bounds=(0,1))
	model.Decision_Y = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, bounds=(0,1))
	model.Decision_Z = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, bounds=(0,1))



	model.Cst = Var(model.SCENARIO)
	model.FRv = Var(model.SCENARIO)
	model.FRv1 = Var(model.SCENARIO)
	model.FRv2 = Var(model.SCENARIO)
	model.Rv = Var(model.SCENARIO)
	model.Rv1 = Var(model.SCENARIO)
	model.Rv2 = Var(model.SCENARIO)
	model.Rv3 = Var(model.SCENARIO)


	def ENPV(model):
		return sum(model.Probability[s] * (model.FRv[s] + model.Rv[s] - model.Cst[s]) for s in model.SCENARIO)
	model.Expected_NPV = Objective(rule=ENPV, sense=maximize)

	
	###Calculate Costs associated with each trial
	def Costs(model,s):
		return model.Cst[s] == sum((1 - (0.025 * (t - 1))) * model.Trial_Cost[i,j] * model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE for t in model.TIME_STEP )
	model.Total_Costs = Constraint(model.SCENARIO,rule=Costs)

	###Calculate the net revenue for each scenario
	def Net_Revenue_rule(model,s):
		return model.Rv[s] == model.Rv1[s] + model.Rv2[s] + model.Rv3[s]
	model.Net_Revenue = Constraint(model.SCENARIO, rule=Net_Revenue_rule)

	def Net_Revenue1_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv1[s] == sum(model.Success[i,s]*(model.Revenue_Max[i] * model.Decision_X[i,last_trial,t,s]) for i in model.PRODUCT for t in model.TIME_STEP) 
	model.Net_Revenue1 = Constraint(model.SCENARIO, rule=Net_Revenue1_rule)

	def Net_Revenue2_rule(model,s):	
		return model.Rv2[s] == sum(-model.Success[i,s]*model.GammaD[i] * sum(model.Decision_Z[i,j,t,s] for j in model.STAGE_GATE if j > 1) for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue2 = Constraint(model.SCENARIO, rule=Net_Revenue2_rule)

	def Net_Revenue3_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv3[s] == sum(-model.Success[i,s]*model.GammaL[i]*(t + model.Duration[i, last_trial]) * model.Decision_X[i,last_trial,t,s] for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue3 = Constraint(model.SCENARIO, rule=Net_Revenue3_rule)

	###Calculate the free Revenue
	def Free_Rev_1_rule(model,s):
		last_time = model.LastTimeStep
		return model.FRv1[s] == sum(model.Success[i,s] * model.Open_Revenue[i,j] * model.Discount_Factor[i,j]* model.Decision_Z[i,j,last_time,s] for i in model.PRODUCT for j in model.STAGE_GATE)
	model.Free_Rev_1 = Constraint(model.SCENARIO, rule=Free_Rev_1_rule)

	def Free_Rev_2_rule(model,s):
		return model.FRv2[s] == sum(model.Success[i,s] * model.Running_Revenue[i,j,t] * model.Discount_Factor[i,j+1]*model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE if j < model.Last_Trial for t in model.TIME_STEP if t > model.LastTimeStep - model.Duration[i,j])
	model.Free_Rev_2 = Constraint(model.SCENARIO, rule=Free_Rev_2_rule)

	def Free_Revenue_rule(model,s):
		return model.FRv[s] == model.FRv1[s] + model.FRv2[s] 
	model.Free_Revenue = Constraint(model.SCENARIO, rule=Free_Revenue_rule)

	### Constraint-- The trial is complete if the trial was started a duration ago
	def Trial_Finish_rule(model,i,j,t,s):
		past_duration = t - model.Duration[i,j]
		if t==1:
			return model.Decision_Y[i,j,t,s] == 0
		elif  t > 1 and  past_duration < 1 :
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s]
		else:
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s] + model.Decision_X[i,j,past_duration,s] 
	model.Trial_Finish = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Trial_Finish_rule)

	### Constraint-- First time step starting rule
	def First_Time_Step_rule(model,i,s):
		return model.Decision_Z[i,1,1,s] == 1 - model.Decision_X[i,1,1,s] 
	model.First_Time_Step = Constraint(model.PRODUCT,model.SCENARIO, rule=First_Time_Step_rule)

	### Constraint--
	def Constraint_1_rule(model,i,t,s):
		if t > 1:
			return model.Decision_Z[i,1,t,s] == model.Decision_Z[i,1,t-1,s] - model.Decision_X[i,1,t,s]
		else:
			return Constraint.Skip
	model.Constraint_1 = Constraint(model.PRODUCT,model.TIME_STEP, model.SCENARIO, rule=Constraint_1_rule)

	### Constraint--
	def Constraint_2_rule(model,i,j,t,s):
		if j > 1 and t-model.Duration[i,j-1] > 0 and t>1:	
			pd = t-model.Duration[i,j-1]
			previous_trial = j-1
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] + model.Decision_X[i,previous_trial,pd,s] - model.Decision_X[i,j,t,s]
		elif j>1 and t>1:
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] - model.Decision_X[i,j,t,s]
		elif t==1 and j>1:
			return model.Decision_Z[i,j,t,s] == -model.Decision_X[i,j,t,s]
		else:
			return Constraint.Skip
	model.Constraint_2 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_2_rule) 

	### Constraint--You can only start each trial once
	def Constraint_3_rule(model,i,j,s):
 		return sum(model.Decision_X[i,j,t,s] for t in model.TIME_STEP) <= 1
	model.Constraint_3 = Constraint(model.PRODUCT,model.STAGE_GATE,model.SCENARIO,rule=Constraint_3_rule)

	### Constraint--
	def Constraint_4_rule(model,i,j,t,s):
		if j > 1:
			previous_trial = j-1
			return sum(model.Decision_X[i,j,tprime,s] for tprime in model.TIME_STEP if tprime <= t) <= model.Decision_Y[i,previous_trial,t,s]
		else:
			return Constraint.Skip
	model.Constraint_4 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_4_rule)

	### Constraint-- Ensures resources are managed correctly
	def Resource_Constraint_rule(model,r,t,s):
		return sum(model.Resources_Required[i,j,r]*model.Decision_X[i,j,tprime,s] for i in model.PRODUCT for j in model.STAGE_GATE for tprime in model.TIME_STEP if tprime > (t - model.Duration[i,j]) and tprime <= t) <= model.Resource_Max[r]
	model.Resource_Constraint = Constraint(model.RESOURCE_TYPE, model.TIME_STEP, model.SCENARIO,rule= Resource_Constraint_rule)

	##DE specific constriants

	def NAC_Constraint_rule(model,i,s):
		return  model.Decision_X[i,1,1,1] == model.Decision_X[i,1,1,s]
	model.NAC_Constraint = Constraint(model.PRODUCT, model.SCENARIO,rule=NAC_Constraint_rule)
	
	def NAC2_Constraint_rule(model,i,j,t,s,sprime):
		if t >1 and sprime > s:
			if (s,sprime) in model.Phi:
				iss = model.phii[s,sprime]
				jss = model.phij[s,sprime]
				return  -model.Decision_Y[iss,jss,t,s] <= model.Decision_X[i,j,t,s]-model.Decision_X[i,j,t,sprime]
			else:
				return Constraint.Skip
		else:
			return Constraint.Skip
	model.NAC2_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,model.SCENARIO,rule=NAC2_Constraint_rule)

	def NAC3_Constraint_rule(model,i,j,t,s,sprime):
		if t >1 and sprime > s:
			if (s,sprime) in model.Phi:
				iss = model.phii[s,sprime]
				jss = model.phij[s,sprime]
				return  model.Decision_Y[iss,jss,t,s] >= model.Decision_X[i,j,t,s]-model.Decision_X[i,j,t,sprime]
			else:
				return Constraint.Skip
		else:
			return Constraint.Skip
	model.NAC3_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, model.SCENARIO,rule=NAC3_Constraint_rule)

	def Fail_Constraint_rule(model,i,j,t,s):
		if model.Outcome[s][prod.index(i)] + 1 < j:
			return model.Decision_X[i,j,t,s] == 0
		else:
			return Constraint.Skip
	model.Fail_Constraint = Constraint(model.PRODUCT,model.STAGE_GATE,model.TIME_STEP,model.SCENARIO, rule=Fail_Constraint_rule)
	
	def Min_Start_Constraint_rule(model,i,j,t,s):
		sumtau = sum(model.Duration[i,k,t,s] for k in model.PRODUCT if k < j)
		if sumtau > t:
			return model.Decision_X[i,j,t,s] == 0
		else:
			return Constraint.Skip
	model.Min_Start_Constraint = Constraint(model.PRODUCT,model.STAGE_GATE,model.TIME_STEP,model.SCENARIO, rule=Min_Start_Constraint_rule)
	return model
	
def deNoNAC(prod,sg,time_step,resource_type,ss,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,probability, success,last_time_step, last_trial, rev_run, open_rev, discounting_factor, outcome):

	model = ConcreteModel()

	##Parameters##
	model.PRODUCT = prod
	model.STAGE_GATE = sg
	model.TIME_STEP = time_step
	model.RESOURCE_TYPE = resource_type
	model.SCENARIO = ss

	model.Resource_Max = resource_max
	model.GammaL = gammaL
	model.GammaD = gammaD
	model.Duration = duration 
	model.Trial_Cost = trial_cost
	model.Resources_Required = resource_required

	model.Revenue_Max = revenue_max
	model.Probability = probability
	model.Success = success
	model.Outcome = outcome

	model.LastTimeStep = last_time_step
	model.Last_Trial = last_trial

	model.Running_Revenue = rev_run

	model.Open_Revenue=open_rev

	model.Discount_Factor= discounting_factor

	
	###Variables###
	model.Decision_X = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)
	model.Decision_Y = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)
	model.Decision_Z = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)



	model.Cst = Var(model.SCENARIO)
	model.FRv = Var(model.SCENARIO)
	model.FRv1 = Var(model.SCENARIO)
	model.FRv2 = Var(model.SCENARIO)
	model.Rv = Var(model.SCENARIO)
	model.Rv1 = Var(model.SCENARIO)
	model.Rv2 = Var(model.SCENARIO)
	model.Rv3 = Var(model.SCENARIO)


	def ENPV(model):
		return sum(model.Probability[s] * (model.FRv[s] + model.Rv[s] - model.Cst[s]) for s in model.SCENARIO)
	model.Expected_NPV = Objective(rule=ENPV, sense=maximize)

	
	###Calculate Costs associated with each trial
	def Costs(model,s):
		return model.Cst[s] == sum((1 - (0.025 * (t - 1))) * model.Trial_Cost[i,j] * model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE for t in model.TIME_STEP )
	model.Total_Costs = Constraint(model.SCENARIO,rule=Costs)

	###Calculate the net revenue for each scenario
	def Net_Revenue_rule(model,s):
		return model.Rv[s] == model.Rv1[s] + model.Rv2[s] + model.Rv3[s]
	model.Net_Revenue = Constraint(model.SCENARIO, rule=Net_Revenue_rule)

	def Net_Revenue1_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv1[s] == sum(model.Success[i,s]*(model.Revenue_Max[i] * model.Decision_X[i,last_trial,t,s]) for i in model.PRODUCT for t in model.TIME_STEP) 
	model.Net_Revenue1 = Constraint(model.SCENARIO, rule=Net_Revenue1_rule)

	def Net_Revenue2_rule(model,s):	
		return model.Rv2[s] == sum(-model.Success[i,s]*model.GammaD[i] * sum(model.Decision_Z[i,j,t,s] for j in model.STAGE_GATE if j > 1) for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue2 = Constraint(model.SCENARIO, rule=Net_Revenue2_rule)

	def Net_Revenue3_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv3[s] == sum(-model.Success[i,s]*model.GammaL[i]*(t + model.Duration[i, last_trial]) * model.Decision_X[i,last_trial,t,s] for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue3 = Constraint(model.SCENARIO, rule=Net_Revenue3_rule)

	###Calculate the free Revenue
	def Free_Rev_1_rule(model,s):
		last_time = model.LastTimeStep
		return model.FRv1[s] == sum(model.Success[i,s] * model.Open_Revenue[i,j] * model.Discount_Factor[i,j]* model.Decision_Z[i,j,last_time,s] for i in model.PRODUCT for j in model.STAGE_GATE)
	model.Free_Rev_1 = Constraint(model.SCENARIO, rule=Free_Rev_1_rule)

	def Free_Rev_2_rule(model,s):
		return model.FRv2[s] == sum(model.Success[i,s] * model.Running_Revenue[i,j,t] * model.Discount_Factor[i,j+1]*model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE if j < model.Last_Trial for t in model.TIME_STEP if t > model.LastTimeStep - model.Duration[i,j])
	model.Free_Rev_2 = Constraint(model.SCENARIO, rule=Free_Rev_2_rule)

	def Free_Revenue_rule(model,s):
		return model.FRv[s] == model.FRv1[s] + model.FRv2[s] 
	model.Free_Revenue = Constraint(model.SCENARIO, rule=Free_Revenue_rule)

	### Constraint-- The trial is complete if the trial was started a duration ago
	def Trial_Finish_rule(model,i,j,t,s):
		past_duration = t - model.Duration[i,j]
		if t==1:
			return model.Decision_Y[i,j,t,s] == 0
		elif  t > 1 and  past_duration < 1 :
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s]
		else:
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s] + model.Decision_X[i,j,past_duration,s] 
	model.Trial_Finish = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Trial_Finish_rule)

	### Constraint-- First time step starting rule
	def First_Time_Step_rule(model,i,s):
		return model.Decision_Z[i,1,1,s] == 1 - model.Decision_X[i,1,1,s] 
	model.First_Time_Step = Constraint(model.PRODUCT,model.SCENARIO, rule=First_Time_Step_rule)

	### Constraint--
	def Constraint_1_rule(model,i,t,s):
		if t > 1:
			return model.Decision_Z[i,1,t,s] == model.Decision_Z[i,1,t-1,s] - model.Decision_X[i,1,t,s]
		else:
			return Constraint.Skip
	model.Constraint_1 = Constraint(model.PRODUCT,model.TIME_STEP, model.SCENARIO, rule=Constraint_1_rule)

	### Constraint--
	def Constraint_2_rule(model,i,j,t,s):
		if j > 1 and t-model.Duration[i,j-1] > 0 and t>1:	
			pd = t-model.Duration[i,j-1]
			previous_trial = j-1
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] + model.Decision_X[i,previous_trial,pd,s] - model.Decision_X[i,j,t,s]
		elif j>1 and t>1:
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] - model.Decision_X[i,j,t,s]
		elif t==1 and j>1:
			return model.Decision_Z[i,j,t,s] == -model.Decision_X[i,j,t,s]
		else:
			return Constraint.Skip
	model.Constraint_2 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_2_rule) 

	### Constraint--You can only start each trial once
	def Constraint_3_rule(model,i,j,s):
 		return sum(model.Decision_X[i,j,t,s] for t in model.TIME_STEP) <= 1
	model.Constraint_3 = Constraint(model.PRODUCT,model.STAGE_GATE,model.SCENARIO,rule=Constraint_3_rule)

	### Constraint--
	def Constraint_4_rule(model,i,j,t,s):
		if j > 1:
			previous_trial = j-1
			return sum(model.Decision_X[i,j,tprime,s] for tprime in model.TIME_STEP if tprime <= t) <= model.Decision_Y[i,previous_trial,t,s]
		else:
			return Constraint.Skip
	model.Constraint_4 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_4_rule)

	### Constraint-- Ensures resources are managed correctly
	def Resource_Constraint_rule(model,r,t,s):
		return sum(model.Resources_Required[i,j,r]*model.Decision_X[i,j,tprime,s] for i in model.PRODUCT for j in model.STAGE_GATE for tprime in model.TIME_STEP if tprime > (t - model.Duration[i,j]) and tprime <= t) <= model.Resource_Max[r]
	model.Resource_Constraint = Constraint(model.RESOURCE_TYPE, model.TIME_STEP, model.SCENARIO,rule= Resource_Constraint_rule)

	##DE specific constriants

	def NAC_Constraint_rule(model,i,s):
		return  model.Decision_X[i,1,1,1] == model.Decision_X[i,1,1,s]
	model.NAC_Constraint = Constraint(model.PRODUCT, model.SCENARIO,rule=NAC_Constraint_rule)
	
		
	def Fail_Constraint_rule(model,i,j,t,s):
		if model.Outcome[s][prod.index(i)] + 1 < j:
			return model.Decision_X[i,j,t,s] == 0
		else:
			return Constraint.Skip
	model.Fail_Constraint = Constraint(model.PRODUCT,model.STAGE_GATE,model.TIME_STEP,model.SCENARIO, rule=Fail_Constraint_rule)
	
	def Min_Start_Constraint_rule(model,i,j,t,s):
		sumtau = sum(model.Duration[i,k,t,s] for k in model.PRODUCT if k < j)
		if sumtau > t:
			return model.Decision_X[i,j,t,s] == 0
		else:
			return Constraint.Skip
	model.Min_Start_Constraint = Constraint(model.PRODUCT,model.STAGE_GATE,model.TIME_STEP,model.SCENARIO, rule=Min_Start_Constraint_rule)
	return model

def SAA(prod,sg,time_step,resource_type,ss,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,probability, success,last_time_step, last_trial, rev_run, open_rev, discounting_factor, phiij, outcome):

	model = ConcreteModel()

	##Parameters##
	model.PRODUCT = prod
	model.STAGE_GATE = sg
	model.TIME_STEP = time_step
	model.RESOURCE_TYPE = resource_type
	model.SCENARIO = ss

	model.Resource_Max = resource_max
	model.GammaL = gammaL
	model.GammaD = gammaD
	model.Duration = duration 
	model.Trial_Cost = trial_cost
	model.Resources_Required = resource_required

	model.Revenue_Max = revenue_max
	model.Probability = probability
	model.Success = success
	model.Outcome = outcome

	model.LastTimeStep = last_time_step
	model.Last_Trial = last_trial

	model.Running_Revenue = rev_run

	model.Open_Revenue=open_rev

	model.Discount_Factor= discounting_factor

	
	model.Phiij = phiij
	

	

	###Variables###
	model.Decision_X = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)
	model.Decision_Y = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)
	model.Decision_Z = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=Binary)



	model.Cst = Var(model.SCENARIO)
	model.FRv = Var(model.SCENARIO)
	model.FRv1 = Var(model.SCENARIO)
	model.FRv2 = Var(model.SCENARIO)
	model.Rv = Var(model.SCENARIO)
	model.Rv1 = Var(model.SCENARIO)
	model.Rv2 = Var(model.SCENARIO)
	model.Rv3 = Var(model.SCENARIO)


	def ENPV(model):
		return sum(model.Probability[s] * (model.FRv[s] + model.Rv[s] - model.Cst[s]) for s in model.SCENARIO)
	model.Expected_NPV = Objective(rule=ENPV, sense=maximize)

	
	###Calculate Costs associated with each trial
	def Costs(model,s):
		return model.Cst[s] == sum((1 - (0.025 * (t - 1))) * model.Trial_Cost[i,j] * model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE for t in model.TIME_STEP )
	model.Total_Costs = Constraint(model.SCENARIO,rule=Costs)

	###Calculate the net revenue for each scenario
	def Net_Revenue_rule(model,s):
		return model.Rv[s] == model.Rv1[s] + model.Rv2[s] + model.Rv3[s]
	model.Net_Revenue = Constraint(model.SCENARIO, rule=Net_Revenue_rule)

	def Net_Revenue1_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv1[s] == sum(model.Success[i,s]*(model.Revenue_Max[i] * model.Decision_X[i,last_trial,t,s]) for i in model.PRODUCT for t in model.TIME_STEP) 
	model.Net_Revenue1 = Constraint(model.SCENARIO, rule=Net_Revenue1_rule)

	def Net_Revenue2_rule(model,s):	
		return model.Rv2[s] == sum(-model.Success[i,s]*model.GammaD[i] * sum(model.Decision_Z[i,j,t,s] for j in model.STAGE_GATE if j > 1) for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue2 = Constraint(model.SCENARIO, rule=Net_Revenue2_rule)

	def Net_Revenue3_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv3[s] == sum(-model.Success[i,s]*model.GammaL[i]*(t + model.Duration[i, last_trial]) * model.Decision_X[i,last_trial,t,s] for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue3 = Constraint(model.SCENARIO, rule=Net_Revenue3_rule)

	###Calculate the free Revenue
	def Free_Rev_1_rule(model,s):
		last_time = model.LastTimeStep
		return model.FRv1[s] == sum(model.Success[i,s] * model.Open_Revenue[i,j] * model.Discount_Factor[i,j]* model.Decision_Z[i,j,last_time,s] for i in model.PRODUCT for j in model.STAGE_GATE)
	model.Free_Rev_1 = Constraint(model.SCENARIO, rule=Free_Rev_1_rule)

	def Free_Rev_2_rule(model,s):
		return model.FRv2[s] == sum(model.Success[i,s] * model.Running_Revenue[i,j,t] * model.Discount_Factor[i,j+1]*model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE if j < model.Last_Trial for t in model.TIME_STEP if t > model.LastTimeStep - model.Duration[i,j])
	model.Free_Rev_2 = Constraint(model.SCENARIO, rule=Free_Rev_2_rule)

	def Free_Revenue_rule(model,s):
		return model.FRv[s] == model.FRv1[s] + model.FRv2[s] 
	model.Free_Revenue = Constraint(model.SCENARIO, rule=Free_Revenue_rule)

	### Constraint-- The trial is complete if the trial was started a duration ago
	def Trial_Finish_rule(model,i,j,t,s):
		past_duration = t - model.Duration[i,j]
		if t==1:
			return model.Decision_Y[i,j,t,s] == 0
		elif  t > 1 and  past_duration < 1 :
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s]
		else:
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s] + model.Decision_X[i,j,past_duration,s] 
	model.Trial_Finish = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Trial_Finish_rule)

	### Constraint-- First time step starting rule
	def First_Time_Step_rule(model,i,s):
		return model.Decision_Z[i,1,1,s] == 1 - model.Decision_X[i,1,1,s] 
	model.First_Time_Step = Constraint(model.PRODUCT,model.SCENARIO, rule=First_Time_Step_rule)

	### Constraint--
	def Constraint_1_rule(model,i,t,s):
		if t > 1:
			return model.Decision_Z[i,1,t,s] == model.Decision_Z[i,1,t-1,s] - model.Decision_X[i,1,t,s]
		else:
			return Constraint.Skip
	model.Constraint_1 = Constraint(model.PRODUCT,model.TIME_STEP, model.SCENARIO, rule=Constraint_1_rule)

	### Constraint--
	def Constraint_2_rule(model,i,j,t,s):
		if j > 1 and t-model.Duration[i,j-1] > 0 and t>1:	
			pd = t-model.Duration[i,j-1]
			previous_trial = j-1
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] + model.Decision_X[i,previous_trial,pd,s] - model.Decision_X[i,j,t,s]
		elif j>1 and t>1:
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] - model.Decision_X[i,j,t,s]
		elif t==1 and j>1:
			return model.Decision_Z[i,j,t,s] == -model.Decision_X[i,j,t,s]
		else:
			return Constraint.Skip
	model.Constraint_2 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_2_rule) 

	### Constraint--You can only start each trial once
	def Constraint_3_rule(model,i,j,s):
 		return sum(model.Decision_X[i,j,t,s] for t in model.TIME_STEP) <= 1
	model.Constraint_3 = Constraint(model.PRODUCT,model.STAGE_GATE,model.SCENARIO,rule=Constraint_3_rule)

	### Constraint--
	def Constraint_4_rule(model,i,j,t,s):
		if j > 1:
			previous_trial = j-1
			return sum(model.Decision_X[i,j,tprime,s] for tprime in model.TIME_STEP if tprime <= t) <= model.Decision_Y[i,previous_trial,t,s]
		else:
			return Constraint.Skip
	model.Constraint_4 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_4_rule)

	### Constraint-- Ensures resources are managed correctly
	def Resource_Constraint_rule(model,r,t,s):
		return sum(model.Resources_Required[i,j,r]*model.Decision_X[i,j,tprime,s] for i in model.PRODUCT for j in model.STAGE_GATE for tprime in model.TIME_STEP if tprime > (t - model.Duration[i,j]) and tprime <= t) <= model.Resource_Max[r]
	model.Resource_Constraint = Constraint(model.RESOURCE_TYPE, model.TIME_STEP, model.SCENARIO,rule= Resource_Constraint_rule)

	##DE specific constriants

	def NAC_Constraint_rule(model,i,s):
		return  model.Decision_X[i,1,1,ss[0]] == model.Decision_X[i,1,1,s]
	model.NAC_Constraint = Constraint(model.PRODUCT, model.SCENARIO,rule=NAC_Constraint_rule)
	
	def NAC2_Constraint_rule(model,i,j,t,s,sprime):
		
		if t > 1:
			if (s,sprime) in model.Phiij:
				return  -1 * sum(model.Decision_Y[iss,jss,t,s] for iss in model.PRODUCT for jss in model.STAGE_GATE if (iss,jss) in model.Phiij[(s,sprime)])  <= model.Decision_X[i,j,t,s]-model.Decision_X[i,j,t,sprime]		
				
			else:
				return Constraint.Skip
		else:
			return Constraint.Skip
	model.NAC2_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,model.SCENARIO, rule=NAC2_Constraint_rule)

	def NAC3_Constraint_rule(model,i,j,t,s,sprime):
		if t >1:
			if (s,sprime) in model.Phiij:
				return  sum(model.Decision_Y[iss,jss,t,s] for iss in model.PRODUCT for jss in model.STAGE_GATE if (iss,jss) in model.Phiij[(s,sprime)]) >= model.Decision_X[i,j,t,s]-model.Decision_X[i,j,t,sprime]	
			else:
				return Constraint.Skip
		else:
			return Constraint.Skip
	model.NAC3_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, model.SCENARIO,rule=NAC3_Constraint_rule)

	def Fail_Constraint_rule(model,i,j,t,s):
		if model.Outcome[s][prod.index(i)] + 1 < j:
			return model.Decision_X[i,j,t,s] == 0
		else:
			return Constraint.Skip
	model.Fail_Constraint = Constraint(model.PRODUCT,model.STAGE_GATE,model.TIME_STEP,model.SCENARIO, rule=Fail_Constraint_rule)
	
	return model

def SAA_LP(prod,sg,time_step,resource_type,ss,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,probability, success,last_time_step, last_trial, rev_run, open_rev, discounting_factor, phiij, outcome):

	model = ConcreteModel()

	##Parameters##
	model.PRODUCT = prod
	model.STAGE_GATE = sg
	model.TIME_STEP = time_step
	model.RESOURCE_TYPE = resource_type
	model.SCENARIO = ss

	model.Resource_Max = resource_max
	model.GammaL = gammaL
	model.GammaD = gammaD
	model.Duration = duration 
	model.Trial_Cost = trial_cost
	model.Resources_Required = resource_required

	model.Revenue_Max = revenue_max
	model.Probability = probability
	model.Success = success
	model.Outcome = outcome

	model.LastTimeStep = last_time_step
	model.Last_Trial = last_trial

	model.Running_Revenue = rev_run

	model.Open_Revenue=open_rev

	model.Discount_Factor= discounting_factor

	
	model.Phiij = phiij
	

	

	###Variables###
	model.Decision_X = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=NonNegativeReals, bounds=(0,1))
	model.Decision_Y = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=NonNegativeReals, bounds=(0,1))
	model.Decision_Z = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, within=NonNegativeReals, bounds=(0,1))



	model.Cst = Var(model.SCENARIO)
	model.FRv = Var(model.SCENARIO)
	model.FRv1 = Var(model.SCENARIO)
	model.FRv2 = Var(model.SCENARIO)
	model.Rv = Var(model.SCENARIO)
	model.Rv1 = Var(model.SCENARIO)
	model.Rv2 = Var(model.SCENARIO)
	model.Rv3 = Var(model.SCENARIO)


	def ENPV(model):
		return sum(model.Probability[s] * (model.FRv[s] + model.Rv[s] - model.Cst[s]) for s in model.SCENARIO)
	model.Expected_NPV = Objective(rule=ENPV, sense=maximize)

	
	###Calculate Costs associated with each trial
	def Costs(model,s):
		return model.Cst[s] == sum((1 - (0.025 * (t - 1))) * model.Trial_Cost[i,j] * model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE for t in model.TIME_STEP )
	model.Total_Costs = Constraint(model.SCENARIO,rule=Costs)

	###Calculate the net revenue for each scenario
	def Net_Revenue_rule(model,s):
		return model.Rv[s] == model.Rv1[s] + model.Rv2[s] + model.Rv3[s]
	model.Net_Revenue = Constraint(model.SCENARIO, rule=Net_Revenue_rule)

	def Net_Revenue1_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv1[s] == sum(model.Success[i,s]*(model.Revenue_Max[i] * model.Decision_X[i,last_trial,t,s]) for i in model.PRODUCT for t in model.TIME_STEP) 
	model.Net_Revenue1 = Constraint(model.SCENARIO, rule=Net_Revenue1_rule)

	def Net_Revenue2_rule(model,s):	
		return model.Rv2[s] == sum(-model.Success[i,s]*model.GammaD[i] * sum(model.Decision_Z[i,j,t,s] for j in model.STAGE_GATE if j > 1) for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue2 = Constraint(model.SCENARIO, rule=Net_Revenue2_rule)

	def Net_Revenue3_rule(model,s):
		last_trial = model.Last_Trial
		return model.Rv3[s] == sum(-model.Success[i,s]*model.GammaL[i]*(t + model.Duration[i, last_trial]) * model.Decision_X[i,last_trial,t,s] for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue3 = Constraint(model.SCENARIO, rule=Net_Revenue3_rule)

	###Calculate the free Revenue
	def Free_Rev_1_rule(model,s):
		last_time = model.LastTimeStep
		return model.FRv1[s] == sum(model.Success[i,s] * model.Open_Revenue[i,j] * model.Discount_Factor[i,j]* model.Decision_Z[i,j,last_time,s] for i in model.PRODUCT for j in model.STAGE_GATE)
	model.Free_Rev_1 = Constraint(model.SCENARIO, rule=Free_Rev_1_rule)

	def Free_Rev_2_rule(model,s):
		return model.FRv2[s] == sum(model.Success[i,s] * model.Running_Revenue[i,j,t] * model.Discount_Factor[i,j+1]*model.Decision_X[i,j,t,s] for i in model.PRODUCT for j in model.STAGE_GATE if j < model.Last_Trial for t in model.TIME_STEP if t > model.LastTimeStep - model.Duration[i,j])
	model.Free_Rev_2 = Constraint(model.SCENARIO, rule=Free_Rev_2_rule)

	def Free_Revenue_rule(model,s):
		return model.FRv[s] == model.FRv1[s] + model.FRv2[s] 
	model.Free_Revenue = Constraint(model.SCENARIO, rule=Free_Revenue_rule)

	### Constraint-- The trial is complete if the trial was started a duration ago
	def Trial_Finish_rule(model,i,j,t,s):
		past_duration = t - model.Duration[i,j]
		if t==1:
			return model.Decision_Y[i,j,t,s] == 0
		elif  t > 1 and  past_duration < 1 :
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s]
		else:
			return model.Decision_Y[i,j,t,s] == model.Decision_Y[i,j,t-1,s] + model.Decision_X[i,j,past_duration,s] 
	model.Trial_Finish = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Trial_Finish_rule)

	### Constraint-- First time step starting rule
	def First_Time_Step_rule(model,i,s):
		return model.Decision_Z[i,1,1,s] == 1 - model.Decision_X[i,1,1,s] 
	model.First_Time_Step = Constraint(model.PRODUCT,model.SCENARIO, rule=First_Time_Step_rule)

	### Constraint--
	def Constraint_1_rule(model,i,t,s):
		if t > 1:
			return model.Decision_Z[i,1,t,s] == model.Decision_Z[i,1,t-1,s] - model.Decision_X[i,1,t,s]
		else:
			return Constraint.Skip
	model.Constraint_1 = Constraint(model.PRODUCT,model.TIME_STEP, model.SCENARIO, rule=Constraint_1_rule)

	### Constraint--
	def Constraint_2_rule(model,i,j,t,s):
		if j > 1 and t-model.Duration[i,j-1] > 0 and t>1:	
			pd = t-model.Duration[i,j-1]
			previous_trial = j-1
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] + model.Decision_X[i,previous_trial,pd,s] - model.Decision_X[i,j,t,s]
		elif j>1 and t>1:
			return model.Decision_Z[i,j,t,s] == model.Decision_Z[i,j,t-1,s] - model.Decision_X[i,j,t,s]
		elif t==1 and j>1:
			return model.Decision_Z[i,j,t,s] == -model.Decision_X[i,j,t,s]
		else:
			return Constraint.Skip
	model.Constraint_2 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_2_rule) 

	### Constraint--You can only start each trial once
	def Constraint_3_rule(model,i,j,s):
 		return sum(model.Decision_X[i,j,t,s] for t in model.TIME_STEP) <= 1
	model.Constraint_3 = Constraint(model.PRODUCT,model.STAGE_GATE,model.SCENARIO,rule=Constraint_3_rule)

	### Constraint--
	def Constraint_4_rule(model,i,j,t,s):
		if j > 1:
			previous_trial = j-1
			return sum(model.Decision_X[i,j,tprime,s] for tprime in model.TIME_STEP if tprime <= t) <= model.Decision_Y[i,previous_trial,t,s]
		else:
			return Constraint.Skip
	model.Constraint_4 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,rule=Constraint_4_rule)

	### Constraint-- Ensures resources are managed correctly
	def Resource_Constraint_rule(model,r,t,s):
		return sum(model.Resources_Required[i,j,r]*model.Decision_X[i,j,tprime,s] for i in model.PRODUCT for j in model.STAGE_GATE for tprime in model.TIME_STEP if tprime > (t - model.Duration[i,j]) and tprime <= t) <= model.Resource_Max[r]
	model.Resource_Constraint = Constraint(model.RESOURCE_TYPE, model.TIME_STEP, model.SCENARIO,rule= Resource_Constraint_rule)

	##DE specific constriants

	def NAC_Constraint_rule(model,i,s):
		return  model.Decision_X[i,1,1,ss[0]] == model.Decision_X[i,1,1,s]
	model.NAC_Constraint = Constraint(model.PRODUCT, model.SCENARIO,rule=NAC_Constraint_rule)
	
	def NAC2_Constraint_rule(model,i,j,t,s,sprime):
		
		if t > 1:
			if (s,sprime) in model.Phiij:
				return  -1 * sum(model.Decision_Y[iss,jss,t,s] for iss in model.PRODUCT for jss in model.STAGE_GATE if (iss,jss) in model.Phiij[(s,sprime)])  <= model.Decision_X[i,j,t,s]-model.Decision_X[i,j,t,sprime]		
				
			else:
				return Constraint.Skip
		else:
			return Constraint.Skip
	model.NAC2_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO,model.SCENARIO, rule=NAC2_Constraint_rule)

	def NAC3_Constraint_rule(model,i,j,t,s,sprime):
		if t >1:
			if (s,sprime) in model.Phiij:
				return  sum(model.Decision_Y[iss,jss,t,s] for iss in model.PRODUCT for jss in model.STAGE_GATE if (iss,jss) in model.Phiij[(s,sprime)]) >= model.Decision_X[i,j,t,s]-model.Decision_X[i,j,t,sprime]	
			else:
				return Constraint.Skip
		else:
			return Constraint.Skip
	model.NAC3_Constraint = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, model.SCENARIO, model.SCENARIO,rule=NAC3_Constraint_rule)

	def Fail_Constraint_rule(model,i,j,t,s):
		if model.Outcome[s][prod.index(i)] + 1 < j:
			return model.Decision_X[i,j,t,s] == 0
		else:
			return Constraint.Skip
	model.Fail_Constraint = Constraint(model.PRODUCT,model.STAGE_GATE,model.TIME_STEP,model.SCENARIO, rule=Fail_Constraint_rule)
	
	def Min_Start_Constraint_rule(model,i,j,t,s):
		sumtau = sum(model.Duration[i,k,t,s] for k in model.PRODUCT if k < j)
		if sumtau > t:
			return model.Decision_X[i,j,t,s] == 0
		else:
			return Constraint.Skip
	model.Min_Start_Constraint = Constraint(model.PRODUCT,model.STAGE_GATE,model.TIME_STEP,model.SCENARIO, rule=Min_Start_Constraint_rule)
	return model

def SingleScenario(prod,sg,time_step,resource_type,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,probability, success,last_time_step, last_trial, rev_run, open_rev, discounting_factor,outcome):

	model = ConcreteModel()

	##Parameters##
	model.PRODUCT = prod
	model.STAGE_GATE = sg
	model.TIME_STEP = time_step
	model.RESOURCE_TYPE = resource_type
	
	model.Resource_Max = resource_max
	model.GammaL = gammaL
	model.GammaD = gammaD
	model.Duration = duration 
	model.Trial_Cost = trial_cost
	model.Resources_Required = resource_required

	model.Revenue_Max = revenue_max
	model.Probability = probability
	model.Success = success
	model.Outcome = outcome

	model.LastTimeStep = last_time_step
	model.Last_Trial = last_trial

	model.Running_Revenue = rev_run

	model.Open_Revenue=open_rev

	model.Discount_Factor= discounting_factor

	###Variables### 
	model.Decision_X = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, bounds=(0,1))
	model.Decision_Y = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, bounds=(0,1))
	model.Decision_Z = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, bounds=(0,1))



	model.Cst = Var()
	model.FRv = Var()
	model.FRv1 = Var()
	model.FRv2 = Var()
	model.Rv = Var()
	model.Rv1 = Var()
	model.Rv2 = Var()
	model.Rv3 = Var()


	def ENPV(model):
		return model.Probability * (model.FRv + model.Rv - model.Cst) 
	model.Expected_NPV = Objective(rule=ENPV, sense=maximize)

	
	###Calculate Costs associated with each trial
	def Costs(model):
		return model.Cst == sum((1 - (0.025 * (t - 1))) * model.Trial_Cost[i,j] * model.Decision_X[i,j,t] for i in model.PRODUCT for j in model.STAGE_GATE for t in model.TIME_STEP )
	model.Total_Costs = Constraint(rule=Costs)

	###Calculate the net revenue for each scenario
	def Net_Revenue_rule(model):
		return model.Rv == model.Rv1 + model.Rv2 + model.Rv3
	model.Net_Revenue = Constraint(rule=Net_Revenue_rule)

	def Net_Revenue1_rule(model):
		last_trial = model.Last_Trial
		return model.Rv1 == sum(model.Success[i]*(model.Revenue_Max[i] * model.Decision_X[i,last_trial,t]) for i in model.PRODUCT for t in model.TIME_STEP) 
	model.Net_Revenue1 = Constraint(rule=Net_Revenue1_rule)

	def Net_Revenue2_rule(model):	
		return model.Rv2 == sum(-model.Success[i]*model.GammaD[i] * sum(model.Decision_Z[i,j,t] for j in model.STAGE_GATE if j > 1) for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue2 = Constraint(rule=Net_Revenue2_rule)

	def Net_Revenue3_rule(model):
		last_trial = model.Last_Trial
		return model.Rv3 == sum(-model.Success[i]*model.GammaL[i]*(t + model.Duration[i, last_trial]) * model.Decision_X[i,last_trial,t] for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue3 = Constraint(rule=Net_Revenue3_rule)

	###Calculate the free Revenue
	def Free_Rev_1_rule(model):
		last_time = model.LastTimeStep
		return model.FRv1 == sum(model.Success[i] * model.Open_Revenue[i,j] * model.Discount_Factor[i,j]* model.Decision_Z[i,j,last_time] for i in model.PRODUCT for j in model.STAGE_GATE)
	model.Free_Rev_1 = Constraint(rule=Free_Rev_1_rule)

	def Free_Rev_2_rule(model):
		return model.FRv2 == sum(model.Success[i] * model.Running_Revenue[i,j,t] * model.Discount_Factor[i,j+1]*model.Decision_X[i,j,t] for i in model.PRODUCT for j in model.STAGE_GATE if j < model.Last_Trial for t in model.TIME_STEP if t > model.LastTimeStep - model.Duration[i,j])
	model.Free_Rev_2 = Constraint(rule=Free_Rev_2_rule)

	def Free_Revenue_rule(model):
		return model.FRv == model.FRv1 + model.FRv2 
	model.Free_Revenue = Constraint(rule=Free_Revenue_rule)

	### Constraint-- The trial is complete if the trial was started a duration ago
	def Trial_Finish_rule(model,i,j,t):
		past_duration = t - model.Duration[i,j]
		if t==1:
			return model.Decision_Y[i,j,t] == 0
		elif  t > 1 and  past_duration < 1 :
			return model.Decision_Y[i,j,t] == model.Decision_Y[i,j,t-1]
		else:
			return model.Decision_Y[i,j,t] == model.Decision_Y[i,j,t-1] + model.Decision_X[i,j,past_duration] 
	model.Trial_Finish = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, rule=Trial_Finish_rule)

	### Constraint-- First time step starting rule
	def First_Time_Step_rule(model,i):
		return model.Decision_Z[i,1,1] == 1 - model.Decision_X[i,1,1] 
	model.First_Time_Step = Constraint(model.PRODUCT,rule=First_Time_Step_rule)

	### Constraint--
	def Constraint_1_rule(model,i,t):
		if t > 1:
			return model.Decision_Z[i,1,t] == model.Decision_Z[i,1,t-1] - model.Decision_X[i,1,t]
		else:
			return Constraint.Skip
	model.Constraint_1 = Constraint(model.PRODUCT,model.TIME_STEP, rule=Constraint_1_rule)

	### Constraint--
	def Constraint_2_rule(model,i,j,t):
		if j > 1 and t-model.Duration[i,j-1] > 0 and t>1:	
			pd = t-model.Duration[i,j-1]
			previous_trial = j-1
			return model.Decision_Z[i,j,t] == model.Decision_Z[i,j,t-1] + model.Decision_X[i,previous_trial,pd] - model.Decision_X[i,j,t]
		elif j>1 and t>1:
			return model.Decision_Z[i,j,t] == model.Decision_Z[i,j,t-1] - model.Decision_X[i,j,t]
		elif t==1 and j>1:
			return model.Decision_Z[i,j,t] == -model.Decision_X[i,j,t]
		else:
			return Constraint.Skip
	model.Constraint_2 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP,rule=Constraint_2_rule) 

	### Constraint--You can only start each trial once
	def Constraint_3_rule(model,i,j):
 		return sum(model.Decision_X[i,j,t] for t in model.TIME_STEP) <= 1
	model.Constraint_3 = Constraint(model.PRODUCT,model.STAGE_GATE,rule=Constraint_3_rule)

	### Constraint--
	def Constraint_4_rule(model,i,j,t):
		if j > 1:
			previous_trial = j-1
			return sum(model.Decision_X[i,j,tprime] for tprime in model.TIME_STEP if tprime <= t) <= model.Decision_Y[i,previous_trial,t]
		else:
			return Constraint.Skip
	model.Constraint_4 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, rule=Constraint_4_rule)

	### Constraint-- Ensures resources are managed correctly
	def Resource_Constraint_rule(model,r,t):
		return sum(model.Resources_Required[i,j,r]*model.Decision_X[i,j,tprime] for i in model.PRODUCT for j in model.STAGE_GATE for tprime in model.TIME_STEP if tprime > (t - model.Duration[i,j]) and tprime <= t) <= model.Resource_Max[r]
	model.Resource_Constraint = Constraint(model.RESOURCE_TYPE, model.TIME_STEP, rule= Resource_Constraint_rule)

	
	return model
	
def SS_PH(rho,w,xbar,CDs,prod,sg,time_step,resource_type,resource_max,gammaL,gammaD,duration,trial_cost,resource_required, revenue_max,probability, success,last_time_step, last_trial, rev_run, open_rev, discounting_factor,outcome):
	model = ConcreteModel()

	##Parameters##
	model.PRODUCT = prod
	model.STAGE_GATE = sg
	model.TIME_STEP = time_step
	model.RESOURCE_TYPE = resource_type
	
	model.Resource_Max = resource_max
	model.GammaL = gammaL
	model.GammaD = gammaD
	model.Duration = duration 
	model.Trial_Cost = trial_cost
	model.Resources_Required = resource_required

	model.Revenue_Max = revenue_max
	model.Probability = probability
	model.Success = success
	model.Outcome = outcome

	model.LastTimeStep = last_time_step
	model.Last_Trial = last_trial

	model.Running_Revenue = rev_run

	model.Open_Revenue=open_rev

	model.Discount_Factor= discounting_factor
	
	### Progressive Hedging Variables
	model.Constrained_Decisions = CDs
	model.x_bar = xbar
	model.w = w

	###Variables###
	model.Decision_X = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, bounds=(0,1))
	model.Decision_Y = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, bounds=(0,1))
	model.Decision_Z = Var(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, bounds=(0,1))

	

	model.Cst = Var()
	model.FRv = Var()
	model.FRv1 = Var()
	model.FRv2 = Var()
	model.Rv = Var()
	model.Rv1 = Var()
	model.Rv2 = Var()
	model.Rv3 = Var()


	def ENPV(model):
		return (model.FRv + model.Rv - model.Cst) - sum(model.w[i,j,t] * model.Decision_X[i,j,t] for (i,j,t) in model.Constrained_Decisions) - rho/2 *sum((model.Decision_X[i,j,t] - model.x_bar[i,j,t])**2 for (i,j,t) in model.Constrained_Decisions)  
	model.Expected_NPV = Objective(rule=ENPV, sense=maximize)
	
	###Calculate Costs associated with each trial
	def Costs(model):
		return model.Cst == sum((1 - (0.025 * (t - 1))) * model.Trial_Cost[i,j] * model.Decision_X[i,j,t] for i in model.PRODUCT for j in model.STAGE_GATE for t in model.TIME_STEP )
	model.Total_Costs = Constraint(rule=Costs)

	###Calculate the net revenue for each scenario
	def Net_Revenue_rule(model):
		return model.Rv == model.Rv1 - model.Rv2 - model.Rv3
	model.Net_Revenue = Constraint(rule=Net_Revenue_rule)
		
	def Net_Revenue1_rule(model):
		last_trial = model.Last_Trial
		return model.Rv1 == sum(model.Success[i]*(model.Revenue_Max[i] * model.Decision_X[i,last_trial,t]) for i in model.PRODUCT for t in model.TIME_STEP) 
	model.Net_Revenue1 = Constraint(rule=Net_Revenue1_rule)

	def Net_Revenue2_rule(model):	
		return model.Rv2 == sum(model.Success[i]*model.GammaD[i] * sum(model.Decision_Z[i,j,t] for j in model.STAGE_GATE if j > 1) for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue2 = Constraint(rule=Net_Revenue2_rule)

	def Net_Revenue3_rule(model):
		last_trial = model.Last_Trial
		return model.Rv3 == sum(model.Success[i]*model.GammaL[i]*(t + model.Duration[i, last_trial]) * model.Decision_X[i,last_trial,t] for i in model.PRODUCT for t in model.TIME_STEP)
	model.Net_Revenue3 = Constraint(rule=Net_Revenue3_rule)

	###Calculate the free Revenue
	def Free_Rev_1_rule(model):
		last_time = model.LastTimeStep
		return model.FRv1 == sum(model.Success[i] * model.Open_Revenue[i,j] * model.Discount_Factor[i,j]* model.Decision_Z[i,j,last_time] for i in model.PRODUCT for j in model.STAGE_GATE)
	model.Free_Rev_1 = Constraint(rule=Free_Rev_1_rule)

	def Free_Rev_2_rule(model):
		return model.FRv2 == sum(model.Success[i] * model.Running_Revenue[i,j,t] * model.Discount_Factor[i,j+1]*model.Decision_X[i,j,t] for i in model.PRODUCT for j in model.STAGE_GATE if j < model.Last_Trial for t in model.TIME_STEP if t > model.LastTimeStep - model.Duration[i,j])
	model.Free_Rev_2 = Constraint( rule=Free_Rev_2_rule)

	def Free_Revenue_rule(model):
		return model.FRv == model.FRv1 + model.FRv2 
	model.Free_Revenue = Constraint(rule=Free_Revenue_rule)

	### Constraint-- The trial is complete if the trial was started a duration ago
	def Trial_Finish_rule(model,i,j,t):
		past_duration = t - model.Duration[i,j]
		if t==1:
			return model.Decision_Y[i,j,t] == 0
		elif  t > 1 and  past_duration < 1 :
			return model.Decision_Y[i,j,t] == model.Decision_Y[i,j,t-1]
		else:
			return model.Decision_Y[i,j,t] == model.Decision_Y[i,j,t-1] + model.Decision_X[i,j,past_duration] 
	model.Trial_Finish = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, rule=Trial_Finish_rule)

	### Constraint-- First time step starting rule
	def First_Time_Step_rule(model,i):
		return model.Decision_Z[i,1,1] == 1 - model.Decision_X[i,1,1] 
	model.First_Time_Step = Constraint(model.PRODUCT,rule=First_Time_Step_rule)

	### Constraint--
	def Constraint_1_rule(model,i,t):
		if t > 1:
			return model.Decision_Z[i,1,t] == model.Decision_Z[i,1,t-1] - model.Decision_X[i,1,t]
		else:
			return Constraint.Skip
	model.Constraint_1 = Constraint(model.PRODUCT,model.TIME_STEP, rule=Constraint_1_rule)

	### Constraint--
	def Constraint_2_rule(model,i,j,t):
		if j > 1 and t-model.Duration[i,j-1] > 0 and t>1:	
			pd = t-model.Duration[i,j-1]
			previous_trial = j-1
			return model.Decision_Z[i,j,t] == model.Decision_Z[i,j,t-1] + model.Decision_X[i,previous_trial,pd] - model.Decision_X[i,j,t]
		elif j>1 and t>1:
			return model.Decision_Z[i,j,t] == model.Decision_Z[i,j,t-1] - model.Decision_X[i,j,t]
		elif t==1 and j>1:
			return model.Decision_Z[i,j,t] == -model.Decision_X[i,j,t]
		else:
			return Constraint.Skip
	model.Constraint_2 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP,rule=Constraint_2_rule) 

	### Constraint--You can only start each trial once
	def Constraint_3_rule(model,i,j):
 		return sum(model.Decision_X[i,j,t] for t in model.TIME_STEP) <= 1
	model.Constraint_3 = Constraint(model.PRODUCT,model.STAGE_GATE,rule=Constraint_3_rule)

	### Constraint--
	def Constraint_4_rule(model,i,j,t):
		if j > 1:
			previous_trial = j-1
			return sum(model.Decision_X[i,j,tprime] for tprime in model.TIME_STEP if tprime <= t) <= model.Decision_Y[i,previous_trial,t]
		else:
			return Constraint.Skip
	model.Constraint_4 = Constraint(model.PRODUCT, model.STAGE_GATE, model.TIME_STEP, rule=Constraint_4_rule)

	### Constraint-- Ensures resources are managed correctly
	def Resource_Constraint_rule(model,r,t):
		return sum(model.Resources_Required[i,j,r]*model.Decision_X[i,j,tprime] for i in model.PRODUCT for j in model.STAGE_GATE for tprime in model.TIME_STEP if tprime > (t - model.Duration[i,j]) and tprime <= t) <= model.Resource_Max[r]
	model.Resource_Constraint = Constraint(model.RESOURCE_TYPE, model.TIME_STEP, rule= Resource_Constraint_rule)


	return model

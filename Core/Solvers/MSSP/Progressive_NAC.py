import os
import sys
import pdb


def Progressive_NAC(fixed_parameters, prod, sg, SS, outcome):
	phiij = {}
	fsNACmontr = {}
	for i in prod:
		fsNACmontr[i] = 0
	
	for fparm in fixed_parameters:
		if fparm[3] == 0:
			pass
		else:
			if fparm[1] == 3:
				pass
			elif fparm[1] > 0:
				#### Generate the list of associated scenarios
				for rlzns in fixed_parameters[fparm]:
					associated_realization = rlzns + [(prod.index(fparm[0]),sg.index(fparm[1]),1)]
					associated_realization1 = rlzns + [(prod.index(fparm[0]),sg.index(fparm[1]),0)]
					
					#### check to see if the associated realization already exists
						
					assn_exist = False
					for ffv in fixed_parameters:
						if ffv[0] == fparm[0] and ffv[1] == fparm[1] + 1 and ffv[3] == 1:
							for jtms in fixed_parameters[ffv]:
								if set(jtms) == set(associated_realization) or set(jtms) == set(associated_realization1):
									assn_exist = True
					
					### If it doesn't add the appropriate NACs
					if assn_exist == False:
						scen_list = []
						for s in SS:
							cntr = 0
							for ktms in associated_realization:
								if ktms[2] == 0:
									if outcome[s][ktms[0]] == ktms[1]: 
										cntr += 1
								else:
									try:
										if outcome[s][ktms[0]] > ktms[1]:
											cntr += 1
									except:
										pdb.set_trace()
							if cntr == len(associated_realization):
								scen_list.append(s)
				
						for s in scen_list:
							for sp in scen_list:
								if s > sp:
									if outcome[s][prod.index(fparm[0])] > outcome[sp][prod.index(fparm[0])]:
										trl = outcome[sp][prod.index(fparm[0])] + 1
										
										if trl == fparm[1] + 1:	
											try:
												if (fparm[0],trl) in phiij[(s,sp)]:
													pass
												else:
													phiij[(s,sp)].append((fparm[0],trl)) 
									
											except:
												phiij[(s,sp)] = [(fparm[0],trl)]
									elif outcome[s][prod.index(fparm[0])] == outcome[sp][prod.index(fparm[0])]:
										pass
									else:
										trl = outcome[s][prod.index(fparm[0])] + 1
										if fparm[1] + 1 == trl:
											try:
												if (fparm[0],trl) in phiij[(s,sp)]:
													pass
												else:
													phiij[(s,sp)].append((fparm[0],trl)) 
									
											except:
												phiij[(s,sp)] = [(fparm[0],trl)]
			
			else:
				pass						
									
									
								
	for fparm in fixed_parameters:
		if fparm[1] == 1 and fparm[3] == 1:
			if fixed_parameters[fparm] == [[]]:
				fsNACmontr[fparm[0]] = 1
				
	"""			
	for itms in fsNACmontr:
		
		### If the first item hasn't been started generate first stage NACs
		if fsNACmontr[itms] == 0:
			
			for s in SS:
				for sp in SS:
					if s > sp:
						
						
						if outcome[s][prod.index(itms)] == outcome[sp][prod.index(itms)]:
							pass
						else:
							
							if outcome[s][prod.index(itms)] > outcome[sp][prod.index(itms)]:
								trl = outcome[sp][prod.index(itms)] + 1
								if trl == 1:	
									try:
										if (itms,trl) in phiij[(s,sp)]:
											pass
										else:
											phiij[(s,sp)].append((itms,trl)) 
									
									except:
										phiij[(s,sp)] = [(itms,trl)]
									
							elif outcome[s][prod.index(itms)] < outcome[sp][prod.index(itms)]:
								trl = outcome[s][prod.index(itms)] + 1
								if trl == 1:
									try:
										if (itms,trl) in phiij[(s,sp)]:
											pass
										else:
											phiij[(s,sp)].append((itms,trl)) 
									
									except:
										phiij[(s,sp)] = [(itms,trl)]
							else:
								pass
	"""
		
	for itms in prod:
		if fsNACmontr[itms] == 1:
			pass
		else:
			for s in SS:
				for sp in SS:
					if s > sp:		
						if outcome[s][prod.index(itms)] == outcome[sp][prod.index(itms)]:
							pass
						else:	
							if outcome[s][prod.index(itms)] > outcome[sp][prod.index(itms)]:
								trl = outcome[sp][prod.index(itms)] + 1
								if trl == 1:	
									try:
										if (itms,trl) in phiij[(s,sp)]:
											pass
										else:
											phiij[(s,sp)].append((itms,trl)) 
										
									except:
										phiij[(s,sp)] = [(itms,trl)]
									
							else:
								trl = outcome[s][prod.index(itms)] + 1
								if trl == 1:
									try:
										if (itms,trl) in phiij[(s,sp)]:
											pass
										else:
											phiij[(s,sp)].append((itms,trl)) 
									
									except:
										phiij[(s,sp)] = [(itms,trl)]
	
	#### Check to ensure diagonals are complete
	for ssp in phiij:
		cntr = 0
		for i in prod:
			if outcome[ssp[0]][prod.index(i)] == outcome[ssp[1]][prod.index(i)]:
				pass
			else:
				cntr += 1
		if cntr == len(phiij[ssp]):
			pass
		else:
			for i in prod:
				if outcome[ssp[0]][prod.index(i)] > outcome[ssp[1]][prod.index(i)]:
					trl = outcome[ssp[1]][prod.index(i)] + 1
					if (i,trl) in phiij[ssp]:
						pass
					else:
						phiij[ssp].append((i,trl))
				elif outcome[ssp[0]][prod.index(i)] < outcome[ssp[1]][prod.index(i)]:
					trl = outcome[ssp[0]][prod.index(i)] + 1
					if (i,trl) in phiij[ssp]:
						pass
					else:
						phiij[ssp].append((i,trl))
				else:
					pass					
	"""									
	#### Double Check NACS for unecessary NACS
	for s in SS:
		for sp in SS:
			if s > sp:
				for ffv in fixed_parameters:
					if ffv[3] == 1:
						for jtms in fixed_parameters[ffv]:
							if len(jtms) == 0:
								### Check NACS for 
								if (s,sp) in phiij:
									if (ffv[0],ffv[1]) in phiij[(s,sp)]:
										phiij[(s,sp)].remove((ffv[0],ffv[1]))
							else:
								### are s and sp sharing the realization
								struth = False
								sptruth = False
								cntr = 0
								for ktms in jtms:
									if ktms[2] == 0:
										if outcome[s][ktms[0]] == ktms[1]: 
											cntr += 1
									else:
										try:
											if outcome[s][ktms[0]] > ktms[1]:
												cntr += 1
										except:
											pdb.set_trace()
								if cntr == len(jtms):
									struth = True
							
								for ktms in jtms:
									if ktms[2] == 0:
										if outcome[sp][ktms[0]] == ktms[1]: 
											cntr += 1
									else:
										try:
											if outcome[sp][ktms[0]] > ktms[1]:
												cntr += 1
										except:
											pdb.set_trace()
								if cntr == len(jtms):
									sptruth = True	
								
								if struth == True and sptruth == True:
									if (s,sp) in phiij:
										if (ffv[0],ffv[1]) in phiij[(s,sp)]:
											phiij[(s,sp)].remove((ffv[0],ffv[1]))
	
	list_to_delete = []									
	for ssp in phiij:
		if len(phiij[ssp]) == 0:
			list_to_delete.append(ssp)	
	
	for itms in list_to_delete:
		del phiij[itms]
	"""					
									
	return phiij		
		

def ALL_NACS(prod, sg, SS, outcome):
	phiij = {}
	
	OC = {}
	for s in SS:
		OC[s] = [] 
		for i in prod:
			OC[s].append(outcome[s][prod.index(i)])
	
	for s in SS:
		for sp in SS:			
			if s > sp:
				for i in prod:
					if OC[s][prod.index(i)] == OC[sp][prod.index(i)]:
						pass
					else:
							
						if OC[s][prod.index(i)] > OC[sp][prod.index(i)]:
							trl = OC[sp][prod.index(i)] + 1
							try:
								phiij[(s,sp)].append((i,trl)) 
									
							except:
								phiij[(s,sp)] = [(i,trl)]
									
						else:
							trl = OC[s][prod.index(i)] + 1
							
							try:
								phiij[(s,sp)].append((i,trl))
									
							except:
								phiij[(s,sp)] = [(i,trl)]						
	return phiij

def ONLY_ADJ(fixed_parameters, prod, sg, SS, outcome):
	phi = {}
	phii = {}
	phij = {}
	OC = {}
	fsNACmontr = {}
	for i in prod:
		fsNACmontr[i] = 0
	
	for s in SS:
		OC[s] = [] 
		for i in prod:
			OC[s].append(outcome[s][prod.index(i)])
			
	for fparm in fixed_parameters:
		if fparm[3] == 0:
			pass
		else:
			if fparm[1] == 3:
				pass
			elif fparm[1] > 0:
				#### Generate the list of associated scenarios
				for rlzns in fixed_parameters[fparm]:
					associated_realization = rlzns + [(prod.index(fparm[0]),sg.index(fparm[1]),1)]
					associated_realization1 = rlzns + [(prod.index(fparm[0]),sg.index(fparm[1]),0)]
						
					assn_exist = False
					for ffv in fixed_parameters:
						if ffv[0] == fparm[0] and ffv[1] == fparm[1] + 1 and ffv[3] == 1:
							for jtms in fixed_parameters[ffv]:
								if set(jtms) == set(associated_realization) or set(jtms) == set(associated_realization1):
									assn_exist = True
					
					### If it doesn't add the appropriate NACs
					if assn_exist == False:
						scen_list = []
						for s in SS:
							cntr = 0
							for ktms in associated_realization:
								if ktms[2] == 0:
									if outcome[s][ktms[0]] == ktms[1]: 
										cntr += 1
								else:
									try:
										if outcome[s][ktms[0]] > ktms[1]:
											cntr += 1
									except:
										pdb.set_trace()
							if cntr == len(associated_realization):
								scen_list.append(s)
				
						for s in scen_list:
							for sp in scen_list:
								if s > sp:
									OCtest = list(OC[s])
									OCtest[prod.index(fparm[0])] += 1
									OCtest2 = list(OC[s])
									OCtest2[prod.index(fparm[0])] += -1
									if OCtest == OC[sp]:
										trl = OC[sp][prod.index(fparm[0])] + 1
										if trl == fparm[1] + 1:
											phi[(s,sp)] = 1
											phii[(s,sp)] = fparm[0]
											phij[(s,sp)] = trl
									if OCtest2 == OC[sp]:
										trl = OC[s][prod.index(fparm[0])] + 1
										if trl == fparm[1] + 1:
											phi[(s,sp)] = 1
											phii[(s,sp)] = fparm[0]
											phij[(s,sp)] = trl
			
			else:
				pass						
									
									
								
	for fparm in fixed_parameters:
		if fparm[1] == 1 and fparm[3] == 1:
			if fixed_parameters[fparm] == [[]]:
				fsNACmontr[fparm[0]] = 1
				

	for itms in prod:
		for s in SS:
			for sp in SS:
				if s > sp:		
					if outcome[s][prod.index(itms)] == outcome[sp][prod.index(itms)]:
						pass
					else:
						matchscen = True
						for pr in prod:
							if pr != itms:
								if outcome[s][prod.index(pr)] != outcome[sp][prod.index(pr)]:
									matchscen = False
							
						if matchscen == True:
							if outcome[s][prod.index(itms)] >  outcome[sp][prod.index(itms)]:
								trl = OC[sp][prod.index(itms)] + 1
								if trl == 1:
									phi[(s,sp)] = 1
									phii[(s,sp)] = itms
									phij[(s,sp)] = trl
							else:
								trl = OC[s][prod.index(itms)] + 1
								if trl == 1:
									phi[(s,sp)] = 1
									phii[(s,sp)] = itms
									phij[(s,sp)] = trl
	if fixed_parameters == {('Drug2', 1, 0, 0): [[]], ('Drug2', 1, 1, 1): [[]], ('Drug1', 1, 0, 0): [[]], ('Drug2', 3, 4, 1): [[(1, 1, 1), (1, 0, 1)]], ('Drug1', 1, 2, 0): [[(1, 0, 0)]], ('Drug1', 1, 3, 0): [[(1, 0, 0)]], ('Drug1', 1, 4, 0): [[(1, 1, 0), (1, 0, 1)], [(1, 0, 0)]], ('Drug2', 2, 2, 1): [[(1, 0, 1)]]}:
		pdb.set_trace()									
									
	return phi, phii, phij

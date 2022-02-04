# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 16:31:04 2021
This file is used to simulate the attack technique vectors. It saves the results in the results folder as python objects using the pickle library.

@author: Leon
"""


from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score
import time
import numpy as np
from multiprocessing import Pool
from functools import partial
import pickle
import os.path
import copy


def calc_ap(simulation, malware):
    return(average_precision_score(malware, simulation))

def calc_aps_mp(simulations, malware):
    start = time.time()
    aps = []
    with Pool(processes=4) as pool:
        aps = pool.map(partial(calc_ap, malware = malware), simulations)
    t = time.time()-start
    print(f"MPTime needed to calculate the average precisions for one Malware based on {N} simulations: {t}s")
    a = max(aps)
    print(f"The maximum obtained average precision is: {a}")
    #plt.hist(aps)
    return aps

def get_sim_att_matrix(malware):
    mal_gt = np.array(get_mal_att_gt()[malware])
    ind = np.where(mal_gt == 1)[0]
    base = np.array(pickle.load(open("simulated_attacks/chi_simulations_base.p", "rb")))
    try:
        sim = np.array(pickle.load(open(f"simulated_attacks/{malware}_sim.p", "rb")))
        aps = pickle.load(open(f"simulated_attacks/{malware}_aps.p", "rb"))
    except:
        sim = np.array(pickle.load(open("simulated_attacks/OSX_Shlayer_sim.p", "rb")))
        aps = pickle.load(open("simulated_attacks/OSX_Shlayer_aps.p", "rb"))
    base[:,ind] = sim
    return base, aps

def create_mal_att_gt(driver):  
    mal_att = []
    mal =[]
    with driver.session() as session:
        result = session.run("MATCH (mal:Malware)--(att:Attack) RETURN mal, att")
        result2 = session.run("MATCH (mal:Malware) RETURN mal")
        for el in result:
            mal_att.append(el)
        for malware in result2:
            mal.append(malware["mal"]["name"])
    
    mal_gt = {}
    gt = [0] * 566
    for malware in mal:
        for el in mal_att:
            if el["mal"]["name"] == malware:
                gt[el["att"].id] = 1
            else:
                pass
        mal_gt[malware] = gt
        gt = [0] * 566  
    pickle.dump(open("used_py_objects/mal_gt.p", "wb"))
    
def get_mal_att_gt():
    return pickle.load(open("used_py_objects/mal_gt.p", "rb"))

if __name__ == '__main__':
    
    base_start = time.time()
    driver = GraphDatabase.driver(uri = "bolt://localhost:7687", auth = ("neo4j", "team"))
    mal_gt = get_mal_att_gt()
    # Simulate vectors for each malware and calculate average precsision
    N = 5000 # Number of vectors for each malware
    cmpl_lvl = 0 # counter to keep track of process

    # Use a base set, adjust only the attacks, that are used in given malware.
    chi_simulations = []
    for i in range(int(N/5)):
        chi_simulations.append(np.clip(np.random.chisquare(1,566)/10, None, 1))
        chi_simulations.append(np.clip(np.random.chisquare(2,566)/10, None, 1))
        chi_simulations.append(np.clip(np.random.chisquare(2,566)/10, None, 1))
        chi_simulations.append(np.clip(np.random.chisquare(3,566)/10, None, 1))
        chi_simulations.append(np.clip(np.random.chisquare(1,566)/10, None, 1))
    if not os.path.isfile("chi_simulations_base.p"):
        pickle.dump(chi_simulations, open("chi_simulations_base.p", "wb"))
    chi_sim_copy= []
    for mals in mal_gt.keys():
        if not os.path.isfile(f"{mals}_sim.p"):
            cmpl_lvl += 1
            print( f"{cmpl_lvl}/473\t{mals}")
            start = time.time()              
            ind_used_att = [i for i, e in enumerate(mal_gt[mals]) if e == 1] # List with all the indices of the attacks used in given malware
            chi_sim_copy = copy.deepcopy(chi_simulations)
            values_for_used_attack = []
            for sim in chi_sim_copy:
                d = []
                for ind in ind_used_att:
                    sim[ind] = 1 - np.clip(np.random.chisquare(2, 1)/10, None, 1)
                    d.append(sim[ind])    
                values_for_used_attack.append(d)
            aps = calc_aps_mp(chi_sim_copy, mal_gt[mals])
            t = time.time()-start
            print(f"Time needed to calculate aps: {t}s")
            try:
                pickle.dump(aps, open( f"{mals}_aps.p", "wb" ))
                pickle.dump(values_for_used_attack, open( f"{mals}_sim.p", "wb" ))
            except:
                pickle.dump(aps, open( "OSX_Shlayer_aps.p", "wb" ))
                pickle.dump(values_for_used_attack, open( "OSX_Shlayer_sim.p", "wb" ))
    
    t = time.time()-base_start
    t = round(t/60,2)
    print(f"Total Execution Time: {t}min")



     # This approach took up 20gb of data
     # for mals in mal_gt.keys():
     #     # if not os.path.isfile(f"{mals}_sim.p"):
     #     if True:
     #         cmpl_lvl += 1
     #         print( f"{cmpl_lvl}/566\t{mals}")
     #         start = time.time()
     #         chi_simulations = []
     #         for i in range(int(N/2)):
     #             chi_simulations.append(np.clip(np.random.chisquare(1,566)/10, None, 1))
     #             chi_simulations.append(np.clip(np.random.chisquare(2,566)/10, None, 1))
     #             chi_simulations.append(np.clip(np.random.chisquare(2,566)/10, None, 1))
     #             chi_simulations.append(np.clip(np.random.chisquare(3,566)/10, None, 1))
     #             chi_simulations.append(np.clip(np.random.chisquare(1,566)/10, None, 1))
     #         t = time.time()-start
     #         ind_used_att = [i for i, e in enumerate(mal_gt[mals]) if e == 1] # List with all the indices of the attacks used in given malware
     #         for sim in chi_simulations:
     #             for ind in ind_used_att:
     #                 sim[ind] = 1 - np.clip(np.random.chisquare(2, 1)/10, None, 1)
     #         print(f"Time needed to create {N} technique probability vectors: {t}s")
     #         aps = calc_aps_mp(chi_simulations, mal_gt[mals])
     #         try:
     #             pickle.dump(aps, open( f"{mals}_aps.p", "wb" ))
     #             pickle.dump(chi_simulations, open( f"{mals}_sim.p", "wb" ))
     #         except:
     #             pickle.dump(aps, open( "OSX_Shlayer_aps.p", "wb" ))
     #             pickle.dump(chi_simulations, open( "OSX_Shlayer_sim.p", "wb" ))
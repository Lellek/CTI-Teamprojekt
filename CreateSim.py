# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 16:31:04 2021

@author: Leon
"""

## Erstellt die "simulations" vektoren und berechnet deren aps

from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score
import time
import numpy as np
from multiprocessing import Pool
from functools import partial
import pickle
import os.path


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

if __name__ == '__main__':
    base_start = time.time()
    # Create the ground truths for each malware
    driver = GraphDatabase.driver(uri = "bolt://localhost:7687", auth = ("neo4j", "team"))
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
    
    
    # Simulate vectors for each malware and calculate average precsision
    N = 10000 # Number of vectors for each malware
    cmpl_lvl = 0 # counter to keep track of process
    for mals in mal_gt.keys():
        if not os.path.isfile(f"{mals}_sim.p"):
            cmpl_lvl += 1
            print( f"{cmpl_lvl}/566\t{mals}")
            start = time.time()
            chi_simulations = []
            for i in range(N):
                chi_simulations.append(np.clip(np.random.chisquare(1,566)/10, None, 1))
            t = time.time()-start
            ind_used_att = [i for i, e in enumerate(mal_gt[mals]) if e == 1] # List with all the indices of the attacks used in given malware
            for sim in chi_simulations:
                for ind in ind_used_att:
                    sim[ind] = 1 - np.clip(np.random.chisquare(3, 1)/10, None, 1)
            print(f"Time needed to create {N} technique probability vectors: {t}s")
            aps = calc_aps_mp(chi_simulations, mal_gt[mals])
            try:
                pickle.dump(aps, open( f"{mals}_aps.p", "wb" ))
                pickle.dump(chi_simulations, open( f"{mals}_sim.p", "wb" ))
            except:
                pickle.dump(aps, open( "OSX_Shlayer_aps.p", "wb" ))
                pickle.dump(chi_simulations, open( "OSX_Shlayer_sim.p", "wb" ))
               

    
    
    t = time.time()-base_start
    t = round(t/60,2)
    print(f"Total Execution Time: {t}min")
# #    for mal in mal_gt.items(): to be done
# #    g = [i for i, e in enumerate(mal_t) if e == 1]
#     test = mal_gt["3PARA RAT"]
#     aps = calc_aps_mp(chi_simulations,test)
#     tests = ['BADNEWS']#, 'Bankshot', 'ADVSTORESHELL', 'Felismus']
    
    # aps = calc_aps(chi_simulations)
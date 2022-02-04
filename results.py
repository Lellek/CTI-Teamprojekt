# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 23:13:14 2022
Loads all the data needed results data.

@author: Leon
"""

import pickle
import numpy as np


mal_opt_def = pickle.load(open("results/mal_opt_def.p", "rb"))
baseline_aps = pickle.load(open("results/baseline_aps.p", "rb"))
baseline = pickle.load(open("results/baseline.p", "rb"))
mal_gt = pickle.load(open("used_py_objects/mal_gt.p", "rb"))
active_defenses = pickle.load(open("results/active_defenses.p", "rb"))




def translate_reduced_def_to_full_def(active_defenses, defense):
    all_defenses = np.zeros((76))
    all_defenses[active_defenses] = defense
    return all_defenses

# These attacks have no defenses mapped to them yet
mal_nan = []
for key in baseline_aps:
    if np.isnan(baseline_aps[key]):
        mal_nan.append(key)
for key in mal_nan:
    del baseline_aps[key]
    del mal_opt_def[key]
        

avg_att_def_aps = {}
for key in mal_opt_def:
    try:
        att_def_aps = pickle.load(open(f"results/{key}_att_def_aps.p", "rb"))
        l = []
        for i in range(11):      
            i = i/10
            if i in att_def_aps[:, 0]:
                ind = np.where(att_def_aps[:, 0] == i)
                avg = np.mean(att_def_aps[ind, 1])
                l.append([i, avg])
        avg_att_def_aps[key] = np.array(l)
    except FileNotFoundError as e:
        print(e)
        
avg_all_att_def_aps = []
for i in range(11):      
    i = i/10
    l = []
    for key in avg_att_def_aps:
        ind = np.where(avg_att_def_aps[key][:, 0] == i)[0]
        if ind.size > 0:
            l.append(avg_att_def_aps[key][ind][0][1])
    avg_all_att_def_aps.append(np.array([i, np.mean(l)]))
    
avg_all_att_def_aps = np.array(avg_all_att_def_aps)

baseline_aps_list = []
for key in baseline_aps:
    baseline_aps_list.append(baseline_aps[key])
    
    
avg_baseline_aps = np.mean(baseline_aps_list)

active_defenses #list with the indices of the defenses that were acutally considered in the algorithm, can be used with get def by id to view the defence in neo4j
mal_opt_def # The opitmal defence strategies for every malware
baseline # the baseline
avg_att_def_aps #Dict containing matrices with the attack and defece techniques for every malware
avg_all_att_def_aps #matrix with attack aps and defense aps for all the malwares
avg_baseline_aps # the average ap for the baseline over all malwares
baseline_aps # dict of all the aps for each malware of the baseline

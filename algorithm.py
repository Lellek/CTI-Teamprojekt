# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 14:47:21 2022
This is the main file. Here we implemented the algorithm and calculated the results.
@author: Leon
"""

import pickle
import numpy as np
from sklearn.metrics import average_precision_score
import random
from CreateSim import get_mal_att_gt, get_sim_att_matrix
from itertools import groupby
from CreateAdj import get_list_of_equal_defs, bin_equal_defs, remove_inferior_defenses, return_adj_matrix_with_active_defenses_only
import time
from multiprocessing import Pool
from functools import partial
import os

FIRST_DEFEND = 673
ALL_DEFENSES = 76




def alg(adj_matrix, attack):
    """
    Calculates the defenses techniques that would be an optimal defense based on given attack.
    
    Parameters
    ----------
    adj_matrix : TYPE
        Matrix connecting the defense to the attack techniques.
    attack : TYPE
        Attack technique vector.

    Returns
    -------
    optimal_defense : TYPE
        Optimal defense technique vector containing a 1 if the technique is used and 0 if not.
    bundled_defenses : TYPE
        List with the defenses that were bundled to one.

    """
    attack = attack.copy()
    adj_matrix = adj_matrix.copy()
    optimal_defense = np.zeros((len(adj_matrix)))
    init_rated_def = np.dot(adj_matrix,attack)
    clustered_defenses = []
    while True:
        rated_def = np.dot(adj_matrix,attack)
        if sum(rated_def) == 0:
            break
        ind_best_def = np.where(rated_def == np.max(rated_def))[0]
        list_of_equal_defs_in_best_def = []
        if len(ind_best_def) > 1:
            t = adj_matrix[ind_best_def]
            t = np.transpose(np.transpose(t)[np.where(attack == 1)[0]])
            list_of_equal_defs_in_best_def = get_list_of_equal_defs(t) #we can bin them now since they will always stay the same
        if list_of_equal_defs_in_best_def:
            list_of_equal_defs = []
            for el in list_of_equal_defs_in_best_def:
                list_of_equal_defs.append(ind_best_def[el])  #prev index of ind_best_def
            #if one of the equal defs was better in the initial rating of the defs it will not be binned, but instead the other nodes will be removed
            for el in list_of_equal_defs:
                if all_equal(init_rated_def[el]):
                    clustered_defenses.append(el)
                    bin_equal_defs(adj_matrix, [el])
                else:
                    not_best_of_equal = np.where(init_rated_def[el] != np.max(init_rated_def[el]))[0]
                    not_best_of_equal = el[not_best_of_equal]
                    adj_matrix[not_best_of_equal] = 0
        else:                           
            ind_best_def = random.choice(ind_best_def)         
            optimal_defense[ind_best_def] = 1 # Or one probably
            ind_att_o_d = np.where(adj_matrix[ind_best_def]==1)[0]
            attack[ind_att_o_d] = 0 # Set values of all attack techniques connected to defense that has been selected

    return optimal_defense, clustered_defenses

# This approach calculated the defense rating by the probability of at least on of the covered attacks being 1
# Since the other way worked pretty well and was implemented first I did not further pursue this
def alg2(adj, sim_attack):
    sim_attack = sim_attack.copy()
    optimal_defense = np.zeros((len(adj_matrix)))
    while True:
        rated_def = np.zeros((len(adj_matrix)))
        for i in range(len(adj_matrix)):
            rating = 1
            for g in range(len(adj_matrix[1])):
                if adj[i, g] == 1:
                    rating = rating * (1-sim_attack[g])
            rating = 1 - rating
            rated_def[i] = rating
        # print(rated_def)
        # print(sum(rated_def))   
        if sum(rated_def) == 0.0: # All defense nodes that help have been used
            print("True")    
            break
        ind_best_def = np.where(rated_def == np.max(rated_def))[0]#IF Multiple nodes have the highest value, we sum up instead and pick by highest Sum
        if len(ind_best_def) > 1: #Fall 1, rated_def, enthält mehrere Maxima, meist im Sicheren Fall
            rated_def_2 = np.dot(adj[ind_best_def], sim_attack) # Bilde Summe für die indices, welche das Maximum enthalten
            ind_best_def_2 = np.where(rated_def_2 == np.max(rated_def_2))[0]
            if len(ind_best_def_2) > 1: #Fall 1.1 Summen enthalten immernoch gleichwertige Elemente
                print("Error")
                ind_best_def = [ind_best_def[ind_best_def_2[0]]] # pick first element
            else:
                ind_best_def = [ind_best_def[ind_best_def_2[0]]]
        ind_best_def = ind_best_def[0]
        # print(ind_best_def, rated_def[ind_best_def])
        optimal_defense[ind_best_def] = rated_def[ind_best_def]
        ind_att_o_d = np.where(adj[ind_best_def]==1)[0]
        sim_attack[ind_att_o_d] = 0
    return optimal_defense

# This function draws n_draws
def alg_with_draw(adj_matrix, sim_attack, n_draws):
    """
    alg_with_draw uses the the algorithm implemented in alg but draws n_draws
    certain attack vectors, from the uncertain sim_attack vector, applies alg
    on those and returns the average occurence of a defense technique.

    Parameters
    ----------
    adj_matrix : TYPE
        Matrix connecting the defense to the attack techniques.
    sim_attack : TYPE
       Attack technique vector.
    n_draws : TYPE
        Number of times drawn from sim_attack.

    Returns
    -------
    avg_def_abs_sim : TYPE
        Defense vector of average occurences.

    """
    abs_sim_attacks = np.empty((len(sim_attack), n_draws))
    for p, i in zip(sim_attack, range(len(sim_attack))):
        abs_sim_attacks[i] = np.random.binomial(1, p, n_draws)
    abs_sim_attacks = np.transpose(abs_sim_attacks)
    def_abs_sim = np.empty((n_draws, len(adj_matrix)))
    for i in range(n_draws):
        def_abs_sim[i], clusters = alg(adj_matrix, abs_sim_attacks[i])
        for cl in clusters:
            def_abs_sim[i][cl] = def_abs_sim[i][cl[0]]/len(cl)
    avg_def_abs_sim = np.mean(def_abs_sim, axis = 0)
    return avg_def_abs_sim
        
def check_for_ambigious_gt(adj_matrix, mal_gt):
    """
    Checks weather or not there is ambigious ground truths, by calculating the gt's multiple times and checking for different results'

    Parameters
    ----------
    adj_matrix : TYPE
        Matrix connecting the defense to the attack techniques.
    mal_gt : TYPE
        Dictionary containg all the malware names as keys and the attack techniques ground truths as values.
    Returns
    -------
    None.

    """
    for key in mal_gt:
        xcss = np.array(mal_gt[key])
        def_gt_prev = alg(adj_matrix, xcss)
        for i in range(1000):
            def_gt = alg(adj_matrix, xcss)
            if not all(def_gt_prev == def_gt):
                print(key)
                break
def all_equal(iterable):
    """
    Checks if all elements of an iterable are equal.

    Parameters
    ----------
    iterable : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

def calculate_mal_opt_def(adj_matrix, mal_gt):
    """
    Calculates the optimal defense technique vectors for all the malwares contained in the mal_gt dictionary.

    Parameters
    ----------
    adj_matrix : TYPE
        Matrix connecting the defense to the attack techniques.
    mal_gt : TYPE
        Dictionary containg all the malware names as keys and the attack techniques ground truths as values.

    Returns
    -------
    mal_opt_def : TYPE
        Dictionary containg all the malware names as keys and the calculated optimal defenses as values.

    """
    mal_opt_def = {}
    mal_clusters = {}
    for key in mal_gt:
        mal_opt_def[key], mal_clusters[key] = alg(adj_matrix, np.array(mal_gt[key]))
    return mal_opt_def, mal_clusters


#amount of times an attack node is used by a malware divided by the total amount of malwares as attack probability
def create_baseline(adj_matrix_mal_att, adj_matrix):
    """
    Calculates a baseline defense vector using the relative frequncy of an attack technique being used in any malware as the attack probability.

    Parameters
    ----------
    adj_matrix_mal_att : TYPE
        Matrix connecting the malwares and attack techniques.
    adj_matrix : TYPE
        Matrix connecting the defense to the attack techniques.

    Returns
    -------
    baseline_defend : TYPE
        The baseline defense technique vector.

    """
    used_mal_for_attack = np.sum(adj_matrix_mal_att, axis = 0)
    baseline_attack = used_mal_for_attack/len(adj_matrix_mal_att)
    baseline_defend = alg_with_draw(adj_matrix, baseline_attack, 10000)
    return baseline_defend

def get_baseline_aps(baseline, mal_opt_def, mal_clusters):
    """
    Calculates the average precision of the baseline for any of the malwares.

    Parameters
    ----------
    baseline : TYPE
        Baseline defense technique vector.
    mal_opt_def : TYPE
        Dictionary containg all the malware names as keys and the calculated optimal defenses as values.

    Returns
    -------
    baseline_aps : TYPE
        List with all the average precisions for the baseline.

    """
    baseline_aps = {}
    for key in mal_opt_def:
        baseline_aps[key] = calculate_ap(baseline, mal_opt_def[key], mal_clusters[key])
    return baseline_aps

def get_def_aps_for_sim(att_sim, att_aps_sim, adj_matrix, opt_def, clusters):
    """
    

    Parameters
    ----------
    att_sim : TYPE
        Simulated attack technique vector.
    att_aps_sim : TYPE
        DESCRIPTION.
    adj_matrix : TYPE
        DESCRIPTION.
    opt_def : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    start = time.time()
    att_aps = []
    def_aps = []
    att_aps_sim = [round(x, 1) for x in att_aps_sim]
    att_aps_sim = np.array(att_aps_sim)
    for i in range(0, 11):
        i = i/10
        indices = np.where(att_aps_sim == i)[0]
        if len(indices) != 0:
            if len(indices) > 50:
                indices = indices[0:50]
            for ind in indices:
                def_sim = alg_with_draw(adj_matrix, att_sim[ind], 200)
                att_aps.append(i)
                def_aps.append(calculate_ap(def_sim, opt_def, clusters))        
    print(str(round(time.time()-start, 2)) + "s")
    return np.transpose(np.array([att_aps, def_aps]))


def calculate_ap(def_sim, opt_def, clusters):
    def_sim = def_sim.copy()
    for cl in clusters:
        def_sim[cl[0]] = np.sum(def_sim[cl])
    return average_precision_score(opt_def, def_sim)
    

def calculate_def_aps_for_malware(malware, mal_opt_def, mal_clusters, adj_matrix):
    if not os.path.isfile(f"results/{malware}_att_def_aps.p"):
        opt_def = mal_opt_def[malware]
        clusters = mal_clusters[malware]
        att_sim, att_aps_sim = get_sim_att_matrix(malware)
        if malware == "OSX/Shlayer":
            pickle.dump(get_def_aps_for_sim(att_sim, att_aps_sim,adj_matrix, opt_def, clusters), open("results/OSX_Shlayer_att_def_aps.p", "wb"))
        else:
            pickle.dump(get_def_aps_for_sim(att_sim, att_aps_sim,adj_matrix, opt_def, clusters), open(f"results/{malware}_att_def_aps.p", "wb"))

def calculate_def_aps_for_all_malwares_mp(mal_opt_def, mal_clusters, adj_matrix):
    malwares = []
    for key in mal_opt_def:
        malwares.append(key)
    with Pool(processes=4) as pool:
        pool.map(partial(calculate_def_aps_for_malware , mal_opt_def = mal_opt_def, mal_clusters = mal_clusters, adj_matrix = adj_matrix), malwares)
        



if __name__ == "__main__":
    adj_matrix = pickle.load(open("used_py_objects/adj_matrix.p", "rb"))
    adj_matrix_mal_att = pickle.load(open("used_py_objects/adj_matrix_mal_att.p", "rb"))
    mal_gt = get_mal_att_gt()
    
    lol = get_list_of_equal_defs(adj_matrix)
    bin_equal_defs(adj_matrix, lol)
    remove_inferior_defenses(adj_matrix)
    active_defenses, adj_matrix = return_adj_matrix_with_active_defenses_only(adj_matrix)   
    
    mal_opt_def, mal_clusters = calculate_mal_opt_def(adj_matrix, mal_gt)
    baseline = create_baseline(adj_matrix_mal_att, adj_matrix)   
    baseline_aps = get_baseline_aps(baseline, mal_opt_def, mal_clusters)
    baseline_2 = np.zeros(len(baseline))
    baseline_2[np.where(baseline > 0.5)[0]] = 1
    baseline_2_aps = get_baseline_aps(baseline_2, mal_opt_def, mal_clusters)
    baseline_3 = np.zeros(len(baseline))
    baseline_3[np.where(baseline > 0.25)[0]] = 1
    baseline_3_aps = get_baseline_aps(baseline_3, mal_opt_def, mal_clusters)
    pickle.dump(baseline, open("results/baseline.p", "wb"))
    pickle.dump(baseline_aps, open("results/baseline_aps.p", "wb"))
    pickle.dump(mal_opt_def, open("results/mal_opt_def.p", "wb"))
    pickle.dump(mal_clusters, open("results/mal_clusters.p", "wb"))    
    pickle.dump(lol, open("results/list_of_equal_defs.p", "wb"))
    pickle.dump(active_defenses, open("results/active_defenses.p", "wb"))
 
    calculate_def_aps_for_all_malwares_mp(mal_opt_def, mal_clusters, adj_matrix)
    
    
    
    
    
    
    
    
    
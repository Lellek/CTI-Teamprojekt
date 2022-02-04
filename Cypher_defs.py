# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 09:54:59 2022
Automatic creation of some useful cyphers. Copy the string to neo4j to see results.
@author: Leon
"""

import numpy as np
FIRST_DEFENSE_ID = 673

def get_def_by_id(def_vector):
    match_cypher = "MATCH "
    where_cypher = " WHERE "
    return_cypher = "RETURN "
    for i in range(len(def_vector)):
        defense = def_vector[i]
        if defense > 0:
            defense_id = FIRST_DEFENSE_ID + i
            match_cypher +=  f"(d{i}), "
            where_cypher += f"id(d{i}) = {defense_id} and "
            return_cypher += f"d{i}, "
    match_cypher = match_cypher[:-2]
    where_cypher = where_cypher[:-4]
    return_cypher = return_cypher[:-2]
    return match_cypher+ " " + where_cypher+ " " + return_cypher

def mark_inferior_equal_def(adj_matrix):
    cnter = 0
    def_inf_equal = np.sum(adj_matrix, axis = 1)
    match_cypher = "MATCH "
    where_cypher = " WHERE "
    set_cypher = "SET "
    for i in range(len(def_inf_equal)):
        defense = def_inf_equal[i]
        if defense != 0:
            cnter += 1
            defense_id = FIRST_DEFENSE_ID + i
            match_cypher +=  f"(d{i}), "
            where_cypher += f"id(d{i}) = {defense_id} and "
            set_cypher += f"d{i}.InfEqFlag = 0, "
    match_cypher = match_cypher[:-2]
    where_cypher = where_cypher[:-4]
    set_cypher = set_cypher[:-2]
    print(cnter)
    return match_cypher+ " " + where_cypher+ " " + set_cypher
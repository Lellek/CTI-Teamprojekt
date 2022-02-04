# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 18:57:02 2022
File where the adjacency matrices are created and reduced to only the relavent parts.
@author: Leon
"""

# Create adjacency matrix
from neo4j import GraphDatabase
import numpy as np
import pickle


driver = GraphDatabase.driver(uri = "bolt://localhost:7687", auth = ("neo4j", "team"))

#creates an adjacency matrix with shape #ofDefenses x #ofAttacks
def create_defense_attack_adj_matrix():
    with driver.session() as session:
        result = session.run("MATCH (d:Defend) RETURN d")
        defs = [record["d"] for record in result]
        result = session.run("MATCH (a:Attack) RETURN a")
        atts = [record["a"] for record in result]
        adj = []
        i = 1
        for a in atts:
            for d in defs:
                print(i)
                i += 1
                result = session.run(f"MATCH (d)--(a) WHERE id(a) = {a.id} AND id(d) = {d.id} RETURN a")
                if len([record for record in result]) == 0:
                    adj.append(0)
                else:
                    adj.append(1)
    adj_matrix = np.resize(np.array(adj), (566, 76))
    adj_matrix = np.transpose(adj_matrix)
    return adj_matrix

def create_malware_attack_adj_matrix():
    len_atts = 0
    len_mals = 0
    with driver.session() as session:
        result = session.run("MATCH (m:Malware) RETURN m")    
        mals = [record["m"] for record in result]
        len_mals = len(mals)
        result = session.run("MATCH (a:Attack) RETURN a")
        atts = [record["a"] for record in result]
        len_atts = len(atts)
        adj = []
        i = 1
        for a in atts:
            for m in mals:
                print(i)
                i += 1
                result = session.run(f"MATCH (m)--(a) WHERE id(a) = {a.id} AND id(m) = {m.id} RETURN a")
                if len([record for record in result]) == 0:
                    adj.append(0)
                else:
                    adj.append(1)
    adj_matrix = np.resize(np.array(adj), (len_atts, len_mals))
    adj_matrix = np.transpose(adj_matrix)
    return adj_matrix

def get_list_of_equal_defs(adj_matrix):
    list_of_equal_defs = []
    for i in range(len(adj_matrix)):
        d = []
        flag = True
        for el in list_of_equal_defs:
            if i in el:
                flag = False
        if flag:
            for g in range(len(adj_matrix)):
                if all(adj_matrix[i] == adj_matrix[g]):
                    d.append(g)
            if len(d) > 1:
                list_of_equal_defs.append(d)               
    return list_of_equal_defs

#set all entries in rows of the adj matrix to 0 if an equal row already exists -> Removing equal defenses from the matrix
def bin_equal_defs(adj_matrix, list_of_equal_defs):
    for equal_defs in list_of_equal_defs:
        for d in equal_defs[1:]:
            adj_matrix[d] = 0

#remove inferior defense techniques: Techniques that are a subset of another technique
def remove_inferior_defenses(adj_matrix):
    inferior_defenses = []
    for i in range(len(adj_matrix)):
        if not all(adj_matrix[i] == 0):
            for g in range(len(adj_matrix)):
                if i != g and not all(adj_matrix[g] == 0):
                    d = adj_matrix[g]-adj_matrix[i]
                    if all(d >= 0):
                        inferior_defenses.append(i)
                        adj_matrix[i] = 0
                        break

def return_adj_matrix_with_active_defenses_only(adj_matrix):
    active_defenses = np.where(np.sum(adj_matrix, axis = 1) > 0)[0]
    return active_defenses, adj_matrix[active_defenses].copy()

if __name__ == "__main__":
    adj_matrix_mal_att = create_malware_attack_adj_matrix()
    # pickle.dump(adj_matrix_mal_att, open("used_py_objects/adj_matrix_mal_att.p", "wb"))
    # pickle.dump(adj_matrix, open("used_py_objects/adj_matrix.p", "wb"))



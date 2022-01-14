# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 18:57:02 2022

@author: Leon
"""

# Create adjacency matrix
from neo4j import GraphDatabase
import numpy as np
import pickle


driver = GraphDatabase.driver(uri = "bolt://localhost:7687", auth = ("neo4j", "team"))

#dauert etwas länger also lieber direkt die den pickle file adj_matrix.p benutzen wie unten
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
col_sums = adj_matrix.sum(axis=0)


pickle.dump(adj_matrix, open("adj_matrix.p", "wb"))


## tests mit der adj matrix
bn = pickle.load(open("C:\\Users\\Leon\\OneDrive - bwedu\\Studium Wing\\7 WS 21_22\\Teamprojekt\\Data\BADNEWS_sim.p", "rb"))
bn_aps =pickle.load(open("C:\\Users\\Leon\\OneDrive - bwedu\\Studium Wing\\7 WS 21_22\\Teamprojekt\\Data\BADNEWS_aps.p", "rb"))
ind = np.argmax(bn_aps)
bn_aps[ind]

test = bn[ind]

res = np.dot(np.transpose(adj_matrix),test)

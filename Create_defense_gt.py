# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 15:51:43 2022

@author: Leon
"""

# Create optimal defense for Malware

from neo4j import GraphDatabase
import pickle
from collections import Counter

#Removes a defense from the subgraph and all its covered attacks, returns reduced subgraph
def remove_def(d, att_def):
    covered_attacks = []
    for record in att_def:
        if d in record:
            covered_attacks.append(record["a"])
    records_to_remove = []
    for record in att_def:
        if any(record["a"] == x for x in covered_attacks):           
            records_to_remove.append(record)
    for record in records_to_remove:
        att_def.remove(record)
    return att_def

##Algorithm 1 Basic Greedy alg
## Find most used Defense, take it, remove all attacks that are covered by this defense from the graph, repeat
def alg1(att_def):
    def_gt = []
    while len(att_def) != 0:
        defs = [record["d"] for record in att_def]
        cnter = Counter(defs)
        d = cnter.most_common(1)[0][0]
        def_gt.append(d) # get the most defense that covers most attacks
        att_def = remove_def(d, att_def)
    return def_gt

##Algorithm 2 Pick Defenses that have to be included, since they are the only one covering a technique first and then basic greedy


def alg2(att_def):
    def_gt = []  
    while True:
        atts = [record["a"] for record in att_def]
        att_once = [el for el, cnt in Counter(atts).items() if cnt==1]
        if len(att_once) == 0:
            break
        for record in att_def:
            if any(record["a"] == att for att in att_once):
                def_gt.append(record["d"])
        for d in def_gt:
            att_def = remove_def(d, att_def)
            
    return list(set(def_gt + alg1(att_def)))
    
    
    
if __name__ == '__main__':   
    mal_gt = pickle.load(open("C:\\Users\\Leon\\OneDrive - bwedu\\Studium Wing\\7 WS 21_22\\Teamprojekt\\Data\mal_gt.p", "rb"))    
    bn_gt = mal_gt["BADNEWS"]   
    
    ##Count the number of Attacks covered by a technique in the given set
    ##Two approaches possible, create one matrix connecting all att tech to def tech
    ##Or pick the def techs based on only the used att techs in a given malware
    ##Maybe a combination is good
    
    driver = GraphDatabase.driver(uri = "bolt://localhost:7687", auth = ("neo4j", "team"))
    alg1_perf = []
    alg2_perf = []
    mals = []
    iterations = 500
    for mal in mal_gt:
        mals.append(mal)
        if iterations == 0:
            break
        iterations = iterations-1
        att_def = []
        defs = []
        atts = []        
        with driver.session() as session:
            result = session.run("MATCH (d:Defend)--(a:Attack)--(m:Malware{name: '" + mal + "'}) RETURN d, a")  
            att_def = [record for record in result]    
        alg1_perf.append(alg1(att_def.copy()))
        alg2_perf.append(alg2(att_def))
    l1 = [len(x) for x in alg1_perf]
    l2 = [len(x) for x in alg2_perf]
    t = [x - y for x, y in zip(l1, l2)]
    
##Alg1 and 2 Perform the same on our set

    
    
    
    
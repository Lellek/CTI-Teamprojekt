# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 10:33:04 2022

@author: Leon
"""

from Create_defense_gt import alg1
from neo4j import GraphDatabase

num = 0



# cypher = "MATCH (d:Defend)--(a:Attack) RETURN a, d"
driver = GraphDatabase.driver(uri = "bolt://localhost:7687", auth = ("neo4j", "team"))

bases = []
with driver.session() as session:
    for num in range(0, 300, 1):
        cypher = "MATCH (a)<-[r:uses]-() WITH a,count(r) AS num WHERE num>" + str(num) + " MATCH (a)--(d:Defend) RETURN d,a,num ORDER BY num desc"
        result = session.run(cypher)  
        att_def = [record for record in result]
        bases.append(alg1(att_def))


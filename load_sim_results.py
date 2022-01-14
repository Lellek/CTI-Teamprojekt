# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 11:36:06 2022

@author: Leon
"""
import pickle
import matplotlib.pyplot as plt



bn_sim = pickle.load(open("C:\\Users\\Leon\\OneDrive - bwedu\\Studium Wing\\7 WS 21_22\\Teamprojekt\\Data\BADNEWS_sim.p", "rb"))
bn_aps = pickle.load(open("C:\\Users\\Leon\\OneDrive - bwedu\\Studium Wing\\7 WS 21_22\\Teamprojekt\\Data\BADNEWS_aps.p", "rb"))
mal_gt = pickle.load(open("C:\\Users\\Leon\\OneDrive - bwedu\\Studium Wing\\7 WS 21_22\\Teamprojekt\\Data\mal_gt.p", "rb"))   
bn_gt = mal_gt["BADNEWS"]

test = bn_sim[0]
ap = bn_aps[0]

plt.hist(bn_aps, 10)

# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 18:16:03 2021

@author: Leon
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score, precision_recall_curve, PrecisionRecallDisplay



y_true = np.array([0, 0, 1, 1])
y_scores = np.array([0.6, 0.8, 0.2, 0.9])

def get_conf_val(y_true, y_scores, TRSH = 0.5):
    y_scores_bin = []
    for i in range(len(y_scores)):
        if y_scores[i] < TRSH:
            y_scores_bin.append(0)
        else:
            y_scores_bin.append(1)
    TP = 0; FN = 0; FP = 0; TN = 0
    for x1, x2 in zip(y_true, y_scores_bin):
        if x1 == 1:
            if x2 == 1:
                TP += 1
            else:
                FN += 1
        else:
            if x2 == 1:
                FP +=1
            else:
                TN += 1
    return TP, FN, FP, TN


#print(f"TP = {TP}", f"FN = {FN}", f"FP = {FP}", f"TN = {TN}")

def p_r_c(y_true, y_scores):
    recalls = [0]
    precisions = [1]
    thresholds = list(y_scores.copy())
    thresholds.sort(reverse=True)
    for threshold in thresholds:
        TP, FN, FP, TN = get_conf_val(y_true, y_scores, threshold)
        recall = TP/(TP+FN)
        precision = TP/(TP + FP)
        recalls.append(recall),
        precisions.append(precision)
    return recalls, precisions, thresholds

recalls, precisions, thresholds = p_r_c(y_true, y_scores)

sk_precisions, sk_recalls, sk_thresholds =  precision_recall_curve(y_true, y_scores)

def get_ap(recalls, precisions):
    ap = 0
    for i in range(len(recalls)-1):
        ap += (recalls[i+1]-recalls[i])*precisions[i+1]
    return ap

sk_ap = average_precision_score(y_true, y_scores)
ap = get_ap(recalls, precisions)
    
disp = PrecisionRecallDisplay(precision=precisions, recall=recalls)
disp.plot()




y_true = np.array([0, 0, 1, 1])
y_scores = np.array([1, 1, 0, 0])
sk_ap = average_precision_score(y_true, y_scores)




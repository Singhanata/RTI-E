# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 20:00:07 2022

@author: krong
"""
import numpy as np
# import ctypes
import os
import time
# import warning
from datetime import datetime
from enum import Enum

class RTIInput():
    TIME_OUT = 3
    def __init__(self, sim, sz, dim, savepath, *args):
        self.log = {}
        self.prior = {}
        self.count = {}
        self.check = (np.zeros(dim[0]),np.zeros(dim[0], dtype=bool))
        self.sim = sim
        self.size = sz
        self.savepath = savepath
        for ar in args:
            self.log[ar] = {}
            self.prior[ar] = {}
            for i in range(dim[0]):
                self.log[ar][i+1] = np.zeros([dim[1], sz])
                self.prior[ar][i+1] = np.zeros([dim[1], 7])
            self.count[ar] = np.zeros((dim[0],dim[1]), dtype=int)
    
    def update(self, vl, key, sDID, idx):
        self.check[1][sDID-1]=False
        self.check[0][sDID-1]=time.time()
        self.log[key][sDID][idx][self.count[key][sDID-1][idx]] = vl
        self.count[key][sDID-1][idx] += 1
        # 01022025:1548: FIX: image report negative value
        normVl = self.prior[key][sDID][idx][PriorIndex.BASE.value]
        sz = self.size
        att = normVl - vl
        # sz = self.size
        # 01022025:1611: FIX: increasing negative value in the image
        if abs(att) < 1: # 05022025:1051:FIX: Baseline include target
            updateNormVl = (normVl * sz + vl)/(sz + 1)
            self.prior[key][sDID][idx][PriorIndex.BASE.value] = updateNormVl
        self.prior[key][sDID][idx][PriorIndex.ATTEN.value] = att
        nei = 2 * idx + 1 if sDID % 2 == 0 else 2 * (idx + 1)
        print("LINK"+ str(sDID)+ "-" + str(nei) 
              + " RSSI:" + str(vl) 
              + " BASE:" + str(self.prior[key][sDID][idx][PriorIndex.BASE.value]) 
              + " ct:" + str(self.count[key][sDID-1][idx]))
        # self.sim.showLink((self.prior, self.count))
        if self.count[key][sDID-1][idx] >= self.size:
            if self.prior[key][sDID][idx][PriorIndex.IS_SET.value] == 0:
                #first round updating values
                self.prior[key][sDID][idx][PriorIndex.STD.value] = np.std(self.log[key][sDID][idx])
                self.prior[key][sDID][idx][PriorIndex.MEAN.value] = np.average(self.log[key][sDID][idx])
                self.prior[key][sDID][idx][PriorIndex.FLOOR.value] = np.average(self.log[key][sDID][idx])
                self.prior[key][sDID][idx][PriorIndex.BASE.value] = np.average(self.log[key][sDID][idx])
                self.prior[key][sDID][idx][PriorIndex.IS_SET.value] = 1
            else: #common value update
                n = self.prior[key][sDID][idx][PriorIndex.TOTAL.value]
                avg_o = self.prior[key][sDID][idx][PriorIndex.MEAN.value]
                std_o = self.prior[key][sDID][idx][PriorIndex.STD.value]
                sz = self.size
                m,s,n = update_mean_std(avg_o, std_o, n, self.log[key][sDID][idx])
                self.prior[key][sDID][idx][PriorIndex.MEAN.value] = m
                self.prior[key][sDID][idx][PriorIndex.STD.value] = s
                self.prior[key][sDID][idx][PriorIndex.TOTAL.value] = n
            parent_folder = self.savepath['rec']
            if self.sim.isRecord():
                parent_folder = os.sep.join([self.sim.savePath, 'N'])
                os.mkdir(parent_folder, exist_ok=True)
            self.prior[key][sDID][idx][0] = self.prior[key][sDID][idx][2]
            self.timeStr = datetime.now().strftime('_%d%m%Y_%H%M%S')
            filename = 'N' + str(sDID) + key + self.timeStr + '.csv'
            filepath = os.sep.join([parent_folder, filename])
            np.savetxt(filepath, self.log[key][sDID], 
                       delimiter = ',', fmt = '%s')
            self.count[key][sDID-1][idx] = 0
            
    def show(self):
        ctime = time.time()
        for i, stamp in enumerate(self.check[0]):
            if (ctime - stamp > RTIInput.TIME_OUT): 
                self.check[1][i]=True
        self.sim.showLink((self.prior, self.count, self.check))
        
class PriorIndex(Enum):
    ATTEN = 0
    BASE = 1
    FLOOR = 2
    MEAN = 3
    STD = 4
    TOTAL = 5
    IS_SET = 6
    
def update_mean_std(old_mean, old_std, old_N, new_samples):
    """Update mean and standard deviation incrementally.
    
    Args:
        old_mean (float): Previous mean.
        old_std (float): Previous standard deviation.
        old_N (int): Previous sample count.
        new_samples (list or np.array): New batch of samples.
        
    Returns:
        tuple: (updated_mean, updated_std, updated_N)
    """
    new_samples = np.array(new_samples, dtype=np.float64)  # Ensure high precision
    n_new = len(new_samples)
    
    if n_new == 0:
        return old_mean, old_std, old_N  # No update needed

    mean_new = np.mean(new_samples)
    var_new = np.var(new_samples, ddof=1)  # Sample variance

    if old_N == 0:
        # First update: directly assign new batch values
        updated_mean = mean_new
        updated_var = var_new
    else:
        N_old = old_N
        mean_old = old_mean
        var_old = old_std ** 2  # Convert SD to variance

        updated_mean = (N_old * mean_old + n_new * mean_new) / (N_old + n_new)

        updated_var = (
            ((N_old - 1) * var_old + (n_new - 1) * var_new + 
             (N_old * n_new / (N_old + n_new)) * (mean_old - mean_new) ** 2) / 
            (N_old + n_new - 1)  # Ensure correct degrees of freedom
        )

    updated_std = np.sqrt(updated_var)  # Convert variance back to SD
    updated_N = old_N + n_new  # Update total count

    return updated_mean, updated_std, updated_N
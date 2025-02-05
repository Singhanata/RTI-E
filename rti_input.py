# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 20:00:07 2022

@author: krong
"""
import numpy as np
import os
# import warning
from datetime import datetime

class RTIInput():
    def __init__(self, sz, dim, savepath, *args):
        self.log = {}
        self.prior = {}
        self.count = {}
        self.size = sz
        self.savepath = savepath
        for ar in args:
            self.log[ar] = {}
            self.prior[ar] = {}
            for i in range(dim[0]):
                self.log[ar][i+1] = np.zeros([dim[1], sz])
                self.prior[ar][i+1] = np.zeros([dim[1], 4])
            self.count[ar] = np.zeros((dim[0],dim[1]), dtype=int)
    
    def update(self, vl, key, sDID, idx):
        self.log[key][sDID][idx][self.count[key][sDID-1][idx]] = vl
        self.count[key][sDID-1][idx] += 1
        # 01022025:1548: FIX: image report negative value
        normVl = self.prior[key][sDID][idx][0]
        sz = self.size
        att = normVl - vl
        # 01022025:1611: FIX: increasing negative value in the image
        if abs(att) < 2: # 05022025:1051:FIX: Baseline include target
            updateNormVl = (normVl * sz + vl)/(sz + 1)
        self.prior[key][sDID][idx][0] = updateNormVl
        self.prior[key][sDID][idx][1] = att
        if self.count[key][sDID-1][idx] >= self.size:
            if self.prior[key][sDID][idx][3] == 0:
                self.prior[key][sDID][idx][2] = np.average(self.log[key][sDID][idx])
                self.prior[key][sDID][idx][0] = np.average(self.log[key][sDID][idx])
                self.prior[key][sDID][idx][3] = 1
            self.prior[key][sDID][idx][0] = self.prior[key][sDID][idx][2]
            self.timeStr = datetime.now().strftime('_%d%m%Y_%H%M%S')
            filename = key + ' N' + str(sDID) + self.timeStr + '.csv'
            filepath = os.sep.join([self.savepath['rec'], filename])
            np.savetxt(filepath, self.log[key][sDID], 
                       delimiter = ',', fmt = '%s')
            self.count[key][sDID-1][idx] = 0



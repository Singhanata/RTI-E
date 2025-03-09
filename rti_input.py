# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 20:00:07 2022

@author: krong
"""
import numpy as np
# import ctypes
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
        att = normVl - vl
        # sz = self.size
        # 01022025:1611: FIX: increasing negative value in the image
        # if abs(att) < 2: # 05022025:1051:FIX: Baseline include target
        #     updateNormVl = (normVl * sz + vl)/(sz + 1)
        #     self.prior[key][sDID][idx][0] = updateNormVl
        self.prior[key][sDID][idx][1] = att
        
        nei = 0
        if sDID % 2 == 0:
            nei = 2 * idx + 1
        else:
            nei = 2 * (idx + 1)
        print("LINK"+ str(sDID)+ "-" + str(nei) 
              + " RSSI:" + str(vl) 
              + " BASE:" + str(self.prior[key][sDID][idx][0]) 
              + " ct:" + str(self.count[key][sDID-1][idx]))
        if self.count[key][sDID-1][idx] >= self.size:
            bsLine = np.average(self.log[key][sDID][idx])
            if self.prior[key][sDID][idx][3] == 0:
                self.prior[key][sDID][idx][2] = bsLine
                self.prior[key][sDID][idx][0] = bsLine
                self.prior[key][sDID][idx][3] = 1
                # ctypes.windll.user32.MessageBoxW(0, "set baseline", "warning", 1)
            self.prior[key][sDID][idx][0] = self.prior[key][sDID][idx][2]
            self.timeStr = datetime.now().strftime('_%d%m%Y_%H%M%S')
            filename = key + ' N' + str(sDID) + self.timeStr + '.csv'
            filepath = os.sep.join([self.savepath['rec'], filename])
            np.savetxt(filepath, self.log[key][sDID], 
                       delimiter = ',', fmt = '%s')
            self.count[key][sDID-1][idx] = 0



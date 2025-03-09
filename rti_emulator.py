# -*- coding: utf-8 -*-
"""
Created on Tue Mar 4 18:34:00 2025

@author: krong
"""
from rti_sim import loadSetting
from rti_input import RTIInput

class RTIEmulator():
    def __init__(self, sim):
        self.sim = sim
        setting = loadSetting(title='LOAD DATA', 
                                       text='Select DATA Folder:')
        dim = sim.getInputDimension()
        self.savePath = sim.process_routine(**setting)
        self.input = RTIInput(sim, setting['sample_size'], dim, self.savepath, 
                              'rssi', 'ir')
    def emulate(self):
        pass

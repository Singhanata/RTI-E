# -*- coding: utf-8 -*-
"""
Created on Wed May 19 14:05:05 2021

@author: krong
"""
from rti_sim import RTISimulation
from rti_sys import RTIConnection, RTIProcess#, ReceiveThread
from rti_exp_position import process_position
from rti_exp_formfactor import process_formfactor
from rti_exp_alpha import process_alpha
from rti_exp_sensor import process_sensor
from rti_exp_voxel import process_voxel
from rti_exp_weightalgorithm import process_weightalgorithm
from rti_animation import process_animate
from rti_emulator import RTIEmulator
import threading
import sys

class RTIProcessThread(threading.Thread):
    def __init__(self, rti, mode, name):
        threading.Thread.__init__(self, daemon=True)
        self.threadID = 1
        self.name = name
        self.mode = mode
        self.sim = rti

    def run(self):
        print("Starting " + self.name)
        rti = self.sim
        mode = self.mode
        if mode == 0:
            # mode0: empirical experiment
            rtiProcess = RTIProcess(rti) 
            rtiConn = RTIConnection(rtiProcess, 'COM3')
            # tReceiveRTI = ReceiveThread(1,
            #                             'Receive Thread',
            #                             1,
            #                             rtiConn)
            # try:
            #     print("Begin .. RTI Update")
            #     tReceiveRTI.start()
            # except:
            #     raise Exception('Cannot Start Thread')
            rtiConn.receive()
        elif mode == 1:
            rtiEmulator = RTIEmulator(rti)
            rtiEmulator.emulate()
            # mode1: Emulate RTI from empirical data
            pass
        elif mode == 21:
            # mode21: animate from simulation
            process_animate(rti)
        elif mode == 22:
            # mode22: investigate effects from position
            process_position(rti)
        elif mode == 23:
            # mode23: investigate effects from formfactor
            process_formfactor(rti)
        elif mode == 24:
            # mode24: investigate effects from alpha coefficient
            process_alpha(rti)
        elif mode == 25:
            # mode25: investigate effects from number of sensors
            process_sensor(rti)
        elif mode == 26:
            # mode26: investigate effects from voxel dimension
            process_voxel(rti)
        elif mode == 27:
            # mode27: investigate effects from weight algorithm
            process_weightalgorithm(rti)
        else:
            # no mode error
            print('Mode not defined')
        print("Exiting " + self.name)

def main():
    rti = RTISimulation()
    mode = rti.init()
    
    tProcess = RTIProcessThread(rti, mode, 'Process Thread')
        
    try:
        print("Begin .. Background Process")
        tProcess.start()
    except:
        raise Exception('Cannot Start Thread')

    rti.run(tProcess)
    
if __name__ == '__main__':
    main()
    sys.exit(0)


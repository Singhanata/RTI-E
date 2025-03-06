# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 22:14:18 2025

@author: krong
"""
from enum import Enum
from rti_eval import RecordIndex

class RTISetting():
    def default():
        setting = {
            'mode' : ModeIndex.EXPERIMENT,
            # scenario setting
            'title': 'RTIExperiment',
            'area_dimension': (4., 7.),
            'voxel_dimension': (0.20, 0.20),
            'sensing_area_position': (4., 7.),
            'n_sensor':12,
            'alpha': 1,
            'schemeType': 'SW',
            'weightalgorithm': 'EX',
            # 'object_dimension': (0.5, 0.5),
            # 'object_type': 'human',
            # sample setting
            'SNR': 4,
            'SNR_mode': 2,
            # 'sample_size' : 100,
            # input setting
            'paramset': ['obj_pos'],
            'paramlabel': ['Object Position'],
            # 'param1' : np.linspace(8, 64, 15),
            # 'param2' : ['LS1','LS2','EL','EX','IN'],
            # output setting
            'gfx_enabled': True,
            'record_enabled': False,
            'der_plot_enabled': False,
            # 'frame_rate': 30
            'resultset': [
                RecordIndex.RMSE_ALL,
                RecordIndex.OBJ_RATIO,
                RecordIndex.DERIVATIVE_RATIO_BN]
        }
        return setting

class ModeIndex(Enum):
    EXPERIMENT = 0
    EMULATION = 1
    ANIMATION = 21
    POSITION_EFFECT = 22
    FORMFACTOR_EFFECT = 23
    ALPHA_EFFECT = 24
    SENSOR_NUMBER_EFFECT = 25
    VOXEL_DIMENSION_EFFECT = 26
    WEIGHTALGORITHM_EFFECT = 27
    @property
    def short(self):
        return {
            ModeIndex.EXPERIMENT : 'EXP',
            ModeIndex.EMULATION : 'Y',
            
            ModeIndex.ANIMATION : 'ANIME',
            ModeIndex.POSITION_EFFECT : 'POS',
            ModeIndex.FORMFACTOR_EFFECT : 'FORM',
            ModeIndex.ALPHA_EFFECT : 'ALPHA',
            ModeIndex.SENSOR_NUMBER_EFFECT : 'SENSOR',
            ModeIndex.VOXEL_DIMENSION_EFFECT : 'VOXEL',
            ModeIndex.WEIGHTALGORITHM_EFFECT : 'WEIGHTALGORITHM'
            }.get(self)
    

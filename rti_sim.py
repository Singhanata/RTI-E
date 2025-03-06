"""
Created on Thu Jun  3 18:44:39 2021

@author: krong
"""
import os
import sys
import subprocess
import threading
from datetime import datetime
from rti_gui import RTIGUI
from rti_setting import RTISetting

from rti_estimator import RTIEstimator
from rti_scheme_sideposition import SidePositionScheme
from rti_scheme_rectangular import RectangularScheme
from rti_cal_linesegment import LineWeightingRTICalculator
from rti_cal_ellipse import EllipseRTICalculator
from rti_cal_expdecay import ExpDecayRTICalculator
from rti_cal_invarea import InvAreaRTICalculator


class RTISimulation():
    def __init__(self):
        tStr = datetime.now().strftime('-%d%m%Y-%H%M%S')
        res_dir = os.sep.join(['results', ('results'+tStr)])
        os.getcwd()
        try:
            os.mkdir(res_dir)
        except:
            print('Folder ' + res_dir + ' is already exist')
        self.res_dir = res_dir
        self.savePath = res_dir
        self.terminate_flag = threading.Event()
        self.save_flag = threading.Event()
        self.execute_flag = threading.Event()
        self.update_flag = threading.Event()
        self.update_flag.set()
        self.setting = RTISetting.default()
        self.gui = RTIGUI(self)

    def getTitle(self, delimiter=',', short=False):
        if short:
            setting = self.estimator.weightCalculator.getSetting()
            title_w = f'A{setting["Width"]}' + delimiter
            title_l = f'{setting["Length"]}' + delimiter
            title_vx = f'V{setting["Voxel Width"]}{setting["Voxel Length"]}' + delimiter
            title_SC = f'N{setting["Sensor Count"]}'
            title_SR = '-'
            title_sch = setting['scheme']
            title_cal = setting['WeightAlgorithm']
        else:
            setting = self.estimator.weightCalculator.getSetting()
            title_w = f'A@({setting["Width"]}' + delimiter
            title_l = f'{setting["Length"]})' + delimiter
            title_vx = f'V@({setting["Voxel Width"]},{setting["Voxel Length"]})' + delimiter
            title_SC = f'N@{setting["Sensor Count"]}'
            title_SR = '-'
            title_sch = setting['scheme']
            title_cal = setting['WeightAlgorithm']

        return (title_w + title_l +
                title_vx + title_SC + title_SR + title_sch + title_cal)

    def process_routine(self, **kw):
        self.setting = kw
        if not ('no_confirm' in kw): 
            self.gui.update(None, ev='Setting')
            kw = self.setting
        self.control()
        ref_pos = (0., 0.)
        if 'reference_position' in kw:
            ref_pos = kw['reference_position']
        a_dim = (10., 10.)
        if 'area_dimension' in kw:
            a_dim = kw['area_dimension']
        wa_dim = a_dim
        if 'sensing_area_dimension' in kw:
            wa_dim = kw['sensing_area_dimension']
        vx_dim = (0.5, 0.5)
        if 'voxel_dimension' in kw:
            vx_dim = kw['voxel_dimension']
        n_s = 20
        if 'n_sensor' in kw:
            n_s = kw['n_sensor']
        schemeType = 'SW'
        if 'schemeType' in kw:
            schemeType = kw['schemeType']
        weightAlgorithm = 'EL'
        if 'weightalgorithm' in kw:
            weightAlgorithm = kw['weightalgorithm']

        if schemeType == 'SW':
            self.scheme = SidePositionScheme(ref_pos,
                                             a_dim[0],    # area_width
                                             a_dim[1],    # area_length
                                             vx_dim[0],   # vx_width
                                             vx_dim[1],   # vx_length
                                             wa_dim[0],   # wa_width
                                             wa_dim[1],   # wa_length
                                             n_s)         # n_sensor
        elif schemeType == 'RE':
            self.scheme = RectangularScheme(ref_pos,
                                            a_dim[0],    # area_width
                                            a_dim[1],    # area_length
                                            vx_dim[0],   # vx_width
                                            vx_dim[1],   # vx_length
                                            wa_dim[0],   # wa_width
                                            wa_dim[1],   # wa_length
                                            n_s)         # n_sensor
        else:
            ValueError('Scheme Type not exist')

        if weightAlgorithm == 'LS1':
            self.calculator = LineWeightingRTICalculator(self.scheme)
        if weightAlgorithm == 'LS2':
            self.calculator = LineWeightingRTICalculator(self.scheme, 2)
        elif weightAlgorithm == 'EL':
            if 'lambda_coeff' in kw:
                self.calculator = EllipseRTICalculator(self.scheme,
                                                       kw['lambda_coeff'])
            else:
                self.calculator = EllipseRTICalculator(self.scheme)
        elif weightAlgorithm == 'EX':
            if 'sigma_w' in kw:
                self.calculator = ExpDecayRTICalculator(self.scheme,
                                                        kw['sigma_w'])
            else:
                self.calculator = ExpDecayRTICalculator(self.scheme)
        elif weightAlgorithm == 'IN':
            if 'lambda_min' in kw:
                self.calculator = InvAreaRTICalculator(self.scheme,
                                                       kw['lambda_min'])
            else:
                self.calculator = InvAreaRTICalculator(self.scheme)
        else:
            ValueError('Weighting Algorithm not exist')

        if 'alpha' in kw:
            self.estimator = RTIEstimator(self.calculator,
                                          kw['alpha'])
        else:
            self.estimator = RTIEstimator(self.calculator)

        fdn = self.res_dir
        title = ''
        if 'title' in kw:
            title += kw['title'] + '-'
        fdn = os.sep.join([fdn, (title + self.getTitle('', True))])
        try:
            os.mkdir(fdn)
        except:
            pass
            # print('Folder ' + fdn + ' is already exist')
        fn_fig = os.sep.join([fdn, 'fig'])
        try:
            os.mkdir(fn_fig)
        except:
            pass
            # print('Folder ' + fn_fig + ' is already exist')
        fn_rec = os.sep.join([fdn, 'rec'])
        try:
            os.mkdir(fn_rec)
        except:
            pass
            # print('Folder ' + fn_rec + ' is already exist')
        fn_con = os.sep.join([fdn, 'conc'])
        try:
            os.mkdir(fn_con)
        except:
            pass
            # print('Folder ' + fn_con + ' is already exist')

        save_path = {}
        save_path['gfx'] = fn_fig
        save_path['rec'] = fn_rec
        save_path['conc'] = fn_con
        print('sim create.. ' + self.getTitle())
        return save_path
    
    def process_input(self, inp):
        print("Process Input")
        l_atten = self.scheme.updateInput(inp)
        iM = {}
        for key, vl in l_atten.items():

            # 01022025:1524: Test not to normalized the image before plot

            iM[key] = self.estimator.calVoxelAtten(vl, False) 
        return l_atten, iM
    
    def coorD(self, **kw):
        if 'axis' in kw:
            axis = kw['axis']
            if axis == 0:
                return self.scheme.coordX
            elif axis == 1:
                return self.scheme.coordY
            else:
                raise ValueError('axis not defined')
        return (self.scheme.coordX, self.scheme.coordY)
    
    def getInputDimension(self):
        return self.scheme.getInputDimension()
    
    def init(self):
        mode  = RTIGUI.getMode()
        self.setting['mode'] = mode
        return mode
    
    def isPlay(self):
        return self.execute_flag.is_set()
    
    def isRecord(self):
        return self.save_flag.is_set()
    
    def stop(self):
        return self.terminate_flag.is_set()
    
    def control(self):
        if self.stop():
            sys.exit()
        self.execute_flag.wait()
        
    def run(self, th):
        while True:
            ev, vl = self.gui.read()
            if ev == 'Exit':
                self.execute_flag.set()
                # self.update_flag.set()
                self.gui.close()
                self.terminate_flag.set()
                th.join()
                sys.exit()
            
            if ev == 'Restart':
                self.execute_flag.set()
                # self.update_flag.set()
                self.gui.close()
                self.terminate_flag.set()
                th.join()
                # python = sys.executable
                # os.execl(python, python, *sys.argv)  
                python = sys.executable
                script = sys.argv[0]  # Current script name
                # Start a new instance of the script
                subprocess.Popen([python, script])  
                # Exit the current instance (but not the Spyder kernel)
                sys.exit(0)
            self.update_flag.set()

    def showIM(self, fig, **kw):
        self.control()
        self.gui.update(fig, **kw, ev='Figure')
                

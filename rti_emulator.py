# -*- coding: utf-8 -*-
"""
Created on Tue Mar 4 18:34:00 2025

@author: krong
"""
import os
import glob
import csv
import ast
import pdb
import numpy as np

from rti_sim import loadSetting
from rti_input import RTIInput
from rti_plot import plotRTIIm

class RTIEmulator():
    def __init__(self, sim):
        self.sim = sim
        sim.execute_flag.set()
        (setting, path) = loadSetting(title='LOAD DATA', 
                                       text='Select DATA Folder:')
        # setting['no_confirm'] = True
        # setting['CheckInput'] = True
        self.dataPath = path
        self.savePath = sim.process_routine(**setting)
        self.dim = sim.getInputDimension()
        self.emulate_order = []
        self.input = RTIInput(sim, setting['sample_size'], self.dim, self.savePath, 
                              'rssi', 'ir')
        # self.sim.emulateInput(self.dataPath)
        
    def emulate(self):
        while not self.sim.isStop():
            self.emulate_order = []
            path, pos, n_sample = self.getInput()
            if (pos is None) and (path is None): break
            print('Follow to get value')
            sample = 0
            self.dataReader = DataReader(path, n_sample)
            while self.sim.isEmul():
                for i in range(self.dim[0]):#emulate packet reception
                    sDID = (i+1)
                    for idx in range(self.dim[1]):
                        self.sim.control()
                        # pdb.set_trace()
                        vl = self.dataReader.sample(sDID, idx, sample)
                        self.input.update(vl, 'rssi', sDID, idx)
                #All Nodes have finished reporting
                self.input.show()
                inp, iM = self.sim.process_input(self.input)
                # pdb.set_trace()
                if self.sim.setting['gfx_enabled']:
                    for ky in iM.keys():
                        if (ky == 'ir'):
                            continue
                        kw = {
                            'path':self.savePath['gfx'],
                            'save':self.savePath['gfx'],
                            'filename':self.sim.getTitle('', True) + '_' + ky,
                            'title':self.sim.getTitle() + "-" + ky,
                            'label':'Rel. Attenuation',
                            'atten_range':self.sim.setting['hmap_range'],
                            'atten':inp[ky]}
                        if self.sim.isRecord():
                            kw['save'] = self.sim.savePath
                        fig = plotRTIIm(self.sim.scheme, iM[ky], **kw)
                        self.sim.showIM(fig, key='Image')
                sample += 1
                if (not n_sample in (0, None)) and (sample >= n_sample): 
                    self.sim.emulate_flag.clear()
                    break
        self.sim.restart()
                
    def getInput(self):
        while True:
            self.sim.control()
            self.sim.emulateInput(self.dataPath)
            self.sim.emulate_flag.wait(timeout=1)
            if len(self.emulate_order) == 0: continue
            path = self.emulate_order[0]
            try:
               # Convert string to tuple using ast.literal_eval
               pos = ast.literal_eval(self.emulate_order[1])
               if not self.emulate_order[2] in ('', 0, None): n_sample = ast.literal_eval(self.emulate_order[2])
               else: n_sample = None 
               # Ensure it's a tuple of numbers
               if (((isinstance(pos, tuple)  and all(isinstance(i, (int, float)) for i in pos)) or pos ==0) and
                   (isinstance(n_sample, int) or (n_sample == None))): break
            except (SyntaxError, ValueError): pass
            # self.sim.gui.warning('Invalid Input')
        print(f'{pos} - {n_sample}')
        return path, pos, n_sample
        
class DataReader:
    def __init__(self, path, n_sample=100):
        self.path = path
        self._create_sample(n_sample)
        
    def _create_sample(self, n_s=100):
        sfL = [entry.name for entry in os.scandir(self.path) if entry.is_dir()]
            
        data = {}
        if sfL == []:
            i, cd = 1, True 
            while cd:
                k = f'N{i}'
                vl = read_and_concatenate_csv_files(self.path, 'rssi ' + k)
                # pdb.set_trace()
                if vl == []: break 
                data[k] = vl
                i += 1
        else: 
            for sf in sfL: data[sf] = read_and_concatenate_csv_files(os.sep.join([self.path, sf]),
                                                                      "rssi " + sf)
        self.data = {}
        for k,vl in data.items():
            self.data[k] = np.zeros([len(data[k]), n_s])
            vl = np.array(vl)
            for i, row in enumerate(vl):
                self.data[k][i] = np.random.choice(row, n_s, replace=True)
    
    def sample(self, sDID, idx, i):
        k = f'N{sDID}'
        n = i % len(self.data[k][idx])
        if (n == 0) and (i==0): self._create_sample()
        return self.data[k][idx][n]
    
def read_and_concatenate_csv_files(folder_path, prefix, delimiter=","):
    """Reads CSV files with a given prefix and concatenates column-wise into a 2D list."""
    
    # Find all CSV files matching the prefix
    file_list = sorted(glob.glob(os.path.join(folder_path, f"{prefix}*.csv")))

    # List to store data column-wise
    columns = []

    for file in file_list:
        try:
            with open(file, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=delimiter)  # Read CSV file
                
                # Read entire file, each row is converted to a list of floats
                numbers = [list(map(float, row)) for row in reader]
                    
                if not len(columns):columns = numbers
                else: columns = [row1 + row2 for row1, row2 in zip(columns, numbers)]
                # Append as a new column
                # columns.append(numbers)
                
                print(f"📄 Processed: {file}")  # Debugging message
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")

    # Handling files with different row lengths by padding with `None`
    # max_rows = max(len(col) for col in columns)  # Find max rows among all files
    # padded_columns = [col + [[None] * len(col[0])] * (max_rows - len(col)) for col in columns]  

    # Transpose columns to rows for correct format
    # data_2d_list = list(map(list, zip(*col)))  # Transpose

    return columns#data_2d_list
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 18:40:48 2025

@author: krong
"""

import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from rti_rec import RecordIndex
import os
import gc

version = __version__ = "0.0.1 Released 15-Feb-2025"

class RTIGUI():
    def __init__(self, sim):
        self.sim = sim
        self.canvas = None     # Persistant storage to avoid garbage collection
        self.N_FIGURE = 10
        self.gc_control = [10,0]
        # Build GUI
        self.window = self._create_gui()
        sg.set_options(keep_on_top=True)
                
        
    def read(self):
        ev, vl = self.window.read()
        if not ev in (sg.TIMEOUT_KEY, '-UPDATEFIG-'):
            print(ev)
            print(vl)
        if (ev == sg.WIN_CLOSED or 
            ev == sg.WIN_CLOSE_ATTEMPTED_EVENT or 
            ev == 'Exit' or 
            (ev == '-BMENU-' and vl['-BMENU-'] == 'Exit')):
            ev = 'Exit'
        
        if (ev == '-UPDATEFIG-'):
            fig = vl['-UPDATEFIG-'][0]
            key = vl['-UPDATEFIG-'][1]
            self.draw_plot(fig, key)
            
        if (ev == '-UPDATESETTING-'):
            self.inputSetting()

        self.menu_listener(ev, vl)
            
        return ev, vl
    
    def menu_listener(self, ev, vl):
            
        if (ev == 'Result'):
            openFolder(self.sim.res_dir)
        
        if ev in ('Play', 'Resume'):
            self.sim.execute_flag.set()
            self.getMenu()
        
        if ev in ('✓ Play', 'Pause'):
            self.sim.execute_flag.clear()
            self.getMenu()
            
        if ev == 'Record':
            fPath = select_open_folder(self.sim.res_dir)
            if not fPath:
                return
            try: 
                os.mkdir(fPath, exist_ok=True)
                self.sim.savePath = fPath
            except:
                Exception('Unsuccessful make directory')
            self.sim.save_flag.set()
            self.getMenu()

        if ev in ('✓ Record', 'Stop'):
            self.sim.save_flag.clear()
            self.getMenu()
            
        if ev == 'Properties':
            self.showSetting()
    
    def showSetting(self):
        data = self.sim.setting
        data['resultset'] = [en.short for en in data['resultset']] 
        table_data = [[key, value] for key, value in data.items()]
        layout = [
            [sg.Table(values=table_data, headings=["Key", "Value"], 
                      auto_size_columns=True,
                      max_col_width=20,
                      justification='left',
                      alternating_row_color='grey',
                      expand_x=True,
                      expand_y=True,
                      num_rows=len(data))],
            [sg.Button("OK")]]

        window = sg.Window("Setting", layout, finalize=True)
        
        while True:
            event, _ = window.read()
            if event in (sg.WIN_CLOSED, "OK"):
                break
        
        window.close()
    
    def inputSetting(self):
        # Default settings dictionary
        setting = self.sim.setting
        
        sampleSize = 0
        n_sensor = 12
        paramset = []
        paramlabel = []
        derEnabled = False
        recEnabled = False
        SNR = 0
        SNRMode = 2
        
        try:
            sampleSize = setting['sample_size']
        except:
            pass
        try:
            n_sensor = setting['n_sensor']
        except:
            pass
        try:
            paramset = setting['paramset']
            paramlabel = setting['paramlabel']
        except:
            pass
        try:
            derEnabled = setting['der_plot_enabled']
        except:
            pass
        try:
            recEnabled = setting['record_enabled']
        except:
            pass
        try:
            SNR = setting['SNR']
            SNRMode = setting['SNR_Mode']
        except:
             pass   
        
        # GUI Layout
        layout = [
            [sg.Text("Title:"), sg.InputText(setting['title'], key="TITLE")],
        
            [sg.Text("Area Dimension (X, Y):"), 
             sg.InputText(setting['area_dimension'][0], key="AREA_X", size=(5,1)), 
             sg.InputText(setting['area_dimension'][1], key="AREA_Y", size=(5,1))],
        
            [sg.Text("Voxel Dimension (X, Y):"), 
             sg.InputText(setting['voxel_dimension'][0], key="VOXEL_X", size=(5,1)), 
             sg.InputText(setting['voxel_dimension'][1], key="VOXEL_Y", size=(5,1))],
        
            [sg.Text("Sensing Area Position (X, Y):"), 
             sg.InputText(setting['sensing_area_position'][0], key="SENSE_X", size=(5,1)), 
             sg.InputText(setting['sensing_area_position'][1], key="SENSE_Y", size=(5,1))],
            [sg.Text("Number of Sensors:"), sg.InputText(n_sensor, key="N_SENSOR", size=(5,1))],
            [sg.Text("Alpha:"), sg.InputText(setting['alpha'], key="ALPHA", size=(5,1))],
            [sg.Text("Scheme Type:"), sg.InputText(setting['schemeType'], key="SCHEME_TYPE")],
            [sg.Text("Weight Algorithm:"), sg.InputText(setting['weightalgorithm'], key="WEIGHT_ALG")],
            [sg.Text("SNR:"), sg.InputText(SNR, key="SNR", size=(5,1))],
            [sg.Text("SNR Mode:"), sg.InputText(SNRMode, key="SNR_MODE", size=(5,1))],
            [sg.Text("Sample Size:"), sg.InputText(sampleSize, key="SAMPLE_SIZE", size=(5,1))],
            [sg.Text("Parameter Set:"), sg.InputText(", ".join(paramset), key="PARAM_SET")],
            [sg.Text("Parameter Label:"), sg.InputText(", ".join(paramlabel), key="PARAM_LABEL")],
            [sg.Checkbox("Graphics Enabled", default=setting['gfx_enabled'], key="GFX_ENABLED")],
            [sg.Checkbox("Derivative Plot Enabled", default=derEnabled, key="DER_ENABLED")],
            [sg.Checkbox("Record Enabled", default=recEnabled, key="REC_ENABLED")],
            [sg.Text("Result Set:")],
            [sg.Checkbox("RMSE", default=(RecordIndex.RMSE_ALL in self.sim.setting['resultset']), key="RMSE"),
             sg.Checkbox("IMAGE", default=(RecordIndex.IMAGE in self.sim.setting['resultset']), key="IMAGE"),
             sg.Checkbox("OBJ_RATIO", default=(RecordIndex.OBJ_RATIO in self.sim.setting['resultset']), key="OBJ_RATIO"),
             sg.Checkbox("OBJ_MEAN", default=(RecordIndex.OBJ_MEAN in self.sim.setting['resultset']), key="OBJ_MEAN"),
             sg.Checkbox("NON_MEAN", default=(RecordIndex.NON_MEAN in self.sim.setting['resultset']), key="NON_MEAN"),
             sg.Checkbox("DERIVATIVE_ABS", default=(RecordIndex.DERIVATIVE_ABS in self.sim.setting['resultset']), key="DERIVATIVE_ABS")],
            [sg.Checkbox("DERIVATIVE_MEAN", default=(RecordIndex.DERIVATIVE_MEAN in self.sim.setting['resultset']), key="DERIVATIVE_MEAN"),
             sg.Checkbox("DERIVATIVE_BORDERRATIO", default=(RecordIndex.DERIVATIVE_BORDERRATIO in self.sim.setting['resultset']), key="DERIVATIVE_BORDERRATIO"),
             sg.Checkbox("DERIVATIVE_NONBORDERRATIO", default=(RecordIndex.DERIVATIVE_NONBORDERRATIO in self.sim.setting['resultset']), key="DERIVATIVE_NONBORDERRATIO"),
             sg.Checkbox("DERIVATIVE_RATIO_XN", default=(RecordIndex.DERIVATIVE_RATIO_XN in self.sim.setting['resultset']), key="DERIVATIVE_RATIO_XN"),
             sg.Checkbox("DERIVATIVE_RATIO_YN", default=(RecordIndex.DERIVATIVE_RATIO_YN in self.sim.setting['resultset']), key="DERIVATIVE_RATIO_YN"),
             sg.Checkbox("DERIVATIVE_RATIO_BN", default=(RecordIndex.DERIVATIVE_RATIO_BN in self.sim.setting['resultset']), key="DERIVATIVE_RATIO_BN")],
        
            [sg.Button("Save"), sg.Button("Cancel")]]

        # Create window
        window = sg.Window("Settings", layout)

        while True:
            event, values = window.read()
        
            if event == sg.WINDOW_CLOSED or event == "Cancel":
                break
        
            if event == "Save":
                # Update settings dictionary
                self.sim.setting['title'] = values["TITLE"]
                self.sim.setting['area_dimension'] = (float(values["AREA_X"]), float(values["AREA_Y"]))
                self.sim.setting['voxel_dimension'] = (float(values["VOXEL_X"]), float(values["VOXEL_Y"]))
                self.sim.setting['sensing_area_position'] = (float(values["SENSE_X"]), float(values["SENSE_Y"]))
                try:
                    self.sim.setting['n_sensor'] = int(float(values["N_SENSOR"]))
                except:
                    Exception('In this mode n_sensor cannot be set')
                self.sim.setting['alpha'] = float(values["ALPHA"])
                self.sim.setting['schemeType'] = values["SCHEME_TYPE"]
                self.sim.setting['weightalgorithm'] = values["WEIGHT_ALG"]
                try:
                    self.sim.setting['SNR'] = float(values["SNR"])
                    self.sim.setting['SNR_mode'] = int(float(values["SNR_MODE"]))
                
                except:
                    Exception('SNR is not defined in this mode')
                try:
                    self.sim.setting['sample_size'] = int(float(values["SAMPLE_SIZE"]))
                except:
                    Exception('sample size cannot be set')
                try:
                    self.sim.setting['paramset'] = values["PARAM_SET"].split(", ")
                    self.sim.setting['paramlabel'] = values["PARAM_LABEL"].split(", ")
                except:
                    Exception('Parameter setting cannot be set')
                self.sim.setting['gfx_enabled'] = values["GFX_ENABLED"]
                try:
                    self.sim.setting['der_plot_enabled'] = values["DER_ENABLED"]
                except:
                    Exception('Derivative plot is not available in this mode')
                try:
                    self.sim.setting['record_enabled'] = values["REC_ENABLED"]
                except:
                    Exception('record enabled option is not defined in this mode')
        
                # Update result set
                try:
                    self.sim.setting['resultset'] = []
                    if values["RMSE"]:
                        self.sim.setting['resultset'].append(RecordIndex.RMSE_ALL)
                    if values["IMAGE"]:
                        self.sim.setting['resultset'].append(RecordIndex.IMAGE)
                    if values["OBJ_RATIO"]:
                        self.sim.setting['resultset'].append(RecordIndex.OBJ_RATIO)
                    if values["OBJ_MEAN"]:
                        self.sim.setting['resultset'].append(RecordIndex.OBJ_MEAN)
                    if values["NON_MEAN"]:
                        self.sim.setting['resultset'].append(RecordIndex.NON_MEAN)
                    if values["DERIVATIVE_ABS"]:
                        self.sim.setting['resultset'].append(RecordIndex.DERIVATIVE_ABS)
                    if values["DERIVATIVE_MEAN"]:
                        self.sim.setting['resultset'].append(RecordIndex.DERIVATIVE_MEAN)
                    if values["DERIVATIVE_BORDERRATIO"]:
                        self.sim.setting['resultset'].append(RecordIndex.DERIVATIVE_BORDERRATIO)
                    if values["DERIVATIVE_NONBORDERRATIO"]:
                        self.sim.setting['resultset'].append(RecordIndex.DERIVATIVE_NONBORDERRATIO)
                    if values["DERIVATIVE_RATIO_XN"]:
                        self.sim.setting['resultset'].append(RecordIndex.DERIVATIVE_RATIO_XN)
                    if values["DERIVATIVE_RATIO_YN"]:
                        self.sim.setting['resultset'].append(RecordIndex.DERIVATIVE_RATIO_YN)
                    if values["DERIVATIVE_RATIO_BN"]:
                        self.sim.setting['resultset'].append(RecordIndex.DERIVATIVE_RATIO_BN)
                except:
                    Exception('resultset cannot be set')
                self.showSetting()
                break
        window.close()

        
    def close(self):
        self.window.close()
        sg.set_options(force_modal_windows=sg.DEFAULT_MODAL_WINDOWS_FORCED)
    
    def update(self, vl, **kw):
        if not self.sim.update_flag.is_set():
            return
        if kw['ev'] == 'Figure':
            self.window.write_event_value('-UPDATEFIG-', (vl, kw['key']))
        if kw['ev'] == 'Setting':
            self.window.write_event_value('-UPDATESETTING-', None)
        self.sim.update_flag.clear()

    def draw_plot(self, fig, key):
        if self.window.was_closed():
            return
        while len(plt.get_fignums()) > self.N_FIGURE:
            plt.close(plt.get_fignums()[0])  # Close the oldest figure

        try:        # Prepare canvas
            canvas_elem = self.window['-IMAGECANVAS-']
            if key == 'Derivative':
                canvas_elem = self.window['-DERCANVAS-']
            elif key == 'Conclusion':
                canvas_elem = self.window['-CONCCANVAS-']
            
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            # for widget in canvas_elem.Widget.winfo_children():
            #     widget.destroy()
            
            self.canvas = FigureCanvasTkAgg(fig, canvas_elem.Widget)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
            canvas_elem.metadata = self.canvas
            # Force cleanup of unused objects
            self.gc_control[1] += 1
            if self.gc_control[1] >= self.gc_control[0]:
                gc.collect()
                self.gc_control[1] = 0
        except:
            Exception('Unsuccessful update Figure')
        
    def getMode():
        # Define the layout
        layout = [
            [sg.Text("Choose an operation mode:")],
            [sg.Radio("Experiment", "RADIO1", key=0)],
            [sg.Radio("Emulation", "RADIO1", key=1)],
            [sg.Radio("Animation", "RADIO1", key=21)],
            [sg.Radio("Simulation Effects of Target Position", "RADIO1", key=22)],
            [sg.Radio("Simulation Effects of Form Factor", "RADIO1", key=23)],
            [sg.Radio("Simulation Effects of Alpha Coefficient", "RADIO1", key=24)],
            [sg.Radio("Simulation Effects of number of sensors", "RADIO1", key=25)],
            [sg.Radio("Simulation Effects of Voxel Dimension", "RADIO1", key=26)],
            [sg.Radio("Simulation Effects of Weight Algorithm", "RADIO1", key=27)],
            [sg.Button("Submit"), sg.Button("Exit")]
        ]
        
        # Create the window
        window = sg.Window("Choice Window", layout)
        
        # Event loop
        while True:
            event, values = window.read()
        
            if event == sg.WINDOW_CLOSED or event == "Exit":
                break
        
            if event == "Submit":
                mode = None
                for key, selected in values.items():
                    if selected:
                        mode = key
                        break
                break
        # Close the window
        window.close()
        return mode

    def getMenu(self):
        sFlag = self.sim.isRecord()
        eFlag = self.sim.isPlay()
        menu_def = [['&Main', ['&Result', f"{'✓ ' if sFlag else ''}&Record",
                        f"{'✓ ' if eFlag else ''}Pl&ay",
                        '---', '&Properties', 'R&estart', 'E&xit']],
                    ['&Analysis', ['&stat', ['&Node', '&Link', '&Output'], '&Conclusion'], ],
                    # ['&Debugger', ['Popout', 'Launch Debugger']],
                    # ['!&Disabled', ['Popout', 'Launch Debugger']],
                    # ['&Toolbar', ['Command &1', 'Command &2', 'Command &3', 'Command &4']],
                    ['&Help', '&About...'], ]
        try:
            self.window['-MENU-'].update(menu_definition=menu_def)  # Update menu
        except:
            Exception('Cannot update Window Menu')
        return menu_def
    
    def getRightClickMenu(self):
        menu = ['&Right', ['Pl&ay',['&Resume', '&Pause'],
                           '&Save', ['&Record', '&Stop'], 
                           '&Result', '&Properties','E&xit',]]
        
        # try:
        #     self.window['-CANVAS-'].TKCanvas.post_menu(
        #        ['&Right', [f"{'✓ ' if eFlag else ''}Pl&ay",
        #                           f"{'✓ ' if sFlag else ''}&Record", 
        #                           '&Menu', 'E&xit', '&Properties']], 
        #        self.window['-CANVAS-'].TKCanvas.winfo_pointerxy())
        # except:
        #     Exception('Cannot update right click Menu')
        return menu
                                      
    def _create_gui(self):
        """
        Create GUI for RTI Experiment
    
        Returns
        -------
        GUI Window
    
        """
        menu_def = self.getMenu()
        # button_menu_def = ['unused', ['&Paste', ['Special', 'Normal', '!Disabled'], 'Undo', 'Exit'], ]
    
        # Build elements in GUI
        sg.set_options(font=("TH SarabunPSK Bold", 14))
        
        # Canvas for Plot
        
        iCanvas = sg.Canvas(key='-IMAGECANVAS-')
        dCanvas = sg.Canvas(key='-DERCANVAS-')
        cCanvas = sg.Canvas(key='-CONCCANVAS-')
        
        
        # Tree Data    
        tData = sg.TreeData()
        
        data = [["", "N1", '', ''],
                ["N1","L1-1", 0, 0],
                ["N1","L1-2", 0, 0],
                ["", "N2", '', ''],
                ["N2","L2-1", 0, 0],
                ["N2","L2-2", 0, 0],
                ["", "N3", '', ''],
                ["N3","L3-1", 0, 0],
                ["N3","L3-2", 0, 0],
                ["", "N4", '', ''],
                ["N4","L4-1", 0, 0],
                ["N4","L4-2", 0, 0],
                ]
        for r in data:
            tData.insert(r[0], r[1], r[1], r[2:])
            
        tr = sg.Tree(data=tData, 
                     headings=["RSSI","ATTEN"],
                     font=("Segoe UI Variable", 10),
                     expand_y=True,
                     key='-NODEINFO-')
        tab1 = sg.Tab('Image', [[iCanvas]])
        tab2 = sg.Tab('Der.', [[dCanvas]])
        tab3 = sg.Tab('Conclusion', [[cCanvas]])
        
        layout = [[]]
        
        layout+= [[sg.Menu(menu_def, key='-MENU-', font=("Segoe UI Variable", 10))],
                  [sg.Text(f'Current Folder : {self.sim.res_dir}')],
                  [sg.pin(sg.Column([[sg.TabGroup([[tab1, tab2, tab3]], 
                                                  key='-TAB_GROUP-')]])), 
                   tr]]
        
        # ly_b = 
        
        window = sg.Window('RTI GUI', layout,
                        # font=('Helvetica', 18),
                        # background_color='black',
                        right_click_menu=self.getRightClickMenu(),
                        # transparent_color= '#9FB8AD',
                        resizable=True,
                        keep_on_top=False,
                        element_justification='c',  # justify contents to the left
                        metadata='My window metadata',
                        finalize=True,
                        # grab_anywhere=True,
                        enable_close_attempted_event=True,
                        modal=False,
                        # ttk_theme=THEME_CLASSIC,
                        # scaling=2,
                        # icon=PSG_DEBUGGER_LOGO,
                        # icon=PSGDebugLogo,
                        )
        
        window._see_through = False
        return window

def openFolder(sdir):
    if os.path.isdir(sdir):
        os.startfile(sdir)  # Open folder in File Explorer
    else:
        sg.popup("Invalid folder selected!")


def select_open_folder(sdir):
    layout = [
        [sg.Text("Select Folder:")],
        [sg.InputText(), sg.FolderBrowse(initial_folder=sdir)],
        [sg.Button("Open"), sg.Button("Cancel")]
    ]
    
    window = sg.Window("Folder Browse", layout)
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, "Cancel"):
            folder_path = None
            break
        
        if event == "Open":
            folder_path = values[0]
            if os.path.isdir(folder_path):
                os.startfile(folder_path)  # Open folder in File Explorer
                break
            else:
                sg.popup("Invalid folder selected!")
    
    window.close()
    return folder_path

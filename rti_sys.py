"""
Created on Fri Sep 30 10:51:00 2022

@author: krong
"""
import serial
import threading
from rti_frame import FrameIndex,FrameSymbol
from rti_input import RTIInput
# from rti_eval import RTIEvaluation, RecordIndex
from rti_plot import plotRTIIm #, plotDerivative

class RTIProcess():
    
    def __init__(self, sim):
        sim.setting = setting = {
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
            'object_type': 'human',
            # sample setting
            'SNR': 4,
            'SNR_mode': 2,
            'sample_size' : 100,
            # input setting
            'paramset': ['obj_pos'],
            'paramlabel': ['Object Position'],
            # 'param1' : np.linspace(8, 64, 15),
            # 'param2' : ['LS1','LS2','EL','EX','IN'],
            # output setting
            'gfx_enabled': True,
            'record_enabled': False,
            'der_plot_enabled': False,
            'hmap_range': (0, 1),
            
            # 'frame_rate': 30
            # 'resultset': [
            #     RecordIndex.RMSE_ALL,
            #     RecordIndex.OBJ_RATIO,
            #     RecordIndex.DERIVATIVE_RATIO_BN]
        }

        self.savepath = sim.process_routine(**setting)
        dim = sim.getInputDimension()
        self.input = RTIInput(sim, setting['sample_size'], dim, self.savepath, 
                              'rssi', 'ir')
        self.ready = False
        self.sUpdate = False
        self.gfx_enabled = setting['gfx_enabled'];
        self.sim = sim
        # self.ev = RTIEvaluation(**setting)

    def control(self):
        return self.sim.control()
                
    def receive_callback(self, msg):
        if msg[FrameIndex.TYPE] == FrameSymbol.CONTENT:
            self.receive_content(msg)
        elif msg[FrameIndex.TYPE] == FrameSymbol.BEACON:
            self.sUpdate = True
        else:
            # print(str(msg[FrameIndex.TYPE]))
            # print(str(FrameSymbol.CONTENT))
            # print(str(FrameSymbol.BEACON))
            # print("receive error")
            print(msg)
        if self.sUpdate:
            self.sUpdate = False
            self.input.show()
            inp, iM = self.sim.process_input(self.input)
            if self.gfx_enabled:
                for ky in iM.keys():
                    if (ky == 'ir'):
                        continue
                    fig = plotRTIIm(self.sim.scheme,
                              iM[ky],
                              path=self.savepath['gfx'],
                              filename=self.sim.getTitle('', True) + '_' + ky,
                              title=self.sim.getTitle() + "-" + ky,
                              label='Rel. Attenuation',
                              atten_range=self.sim.setting['hmap_range'],
                              atten=inp[ky])
                    self.sim.showIM(fig, key='Image')
    
    def receive_content(self, msg):
        # print(msg)
        # msgID = int.from_bytes(msg[FrameIndex.ID])
        # sNID = msg[FrameIndex.sNID]
        sDID = msg[FrameIndex.sDID] - FrameSymbol.ID_OFFSET
        print('NODE ID:' + str(sDID))
        # print('NEXT ID:' + str(sNID))
        l = int.from_bytes(msg[FrameIndex.LENGTH_START:FrameIndex.MASK], 
                           "little", signed=True)
        print(l)
        mask = int.from_bytes(msg[FrameIndex.MASK:FrameIndex.PAYLOAD], 
                              "little", signed=True)
        print(mask)
        if mask == FrameSymbol.MASK:
            n = int(l/2-1)
            ptr = FrameIndex.PAYLOAD
            for i in range(n):
                rssi_vl = int.from_bytes(msg[ptr:(ptr+FrameSymbol.SIZE)], 
                                         "little", signed=True)
                ptr+=FrameSymbol.SIZE
                print("RSSI: " +  str(rssi_vl))
                self.input.update(rssi_vl, 'rssi', sDID, i)
            mask = int.from_bytes(msg[ptr:(ptr+FrameSymbol.SIZE)], 
                                  "little", signed=True)
            ptr+=FrameSymbol.SIZE
            if mask == FrameSymbol.MASK:
                for i in range(n):
                    ir_vl = int.from_bytes(msg[ptr:(ptr+FrameSymbol.SIZE)], 
                                           "little", signed=True)
                    # print("IR:" + str(ir_vl))
                    ptr+=FrameSymbol.SIZE
                    self.input.update(ir_vl, 'ir', sDID, i)
                mask = int.from_bytes(msg[ptr:(ptr+FrameSymbol.SIZE)], 
                                      "little", signed=True)
                ptr+=FrameSymbol.SIZE
                if mask != FrameSymbol.MASK:
                    print('END MASK not detected')
            else:
                print('IR MASK not detected')
        else:
            print('RSSI MASK not detected')
    
class ReceiveThread(threading.Thread):
    def __init__(self, threadID, name, counter, rtiConn):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.rtiConn = rtiConn

    def run(self):
        print("Starting " + self.name)
        self.rtiConn.receive()
        print("Exiting " + self.name)


class RTIConnection():
    MAX_BUFFER_SIZE = 100
    THRESHOLD_LOG_LORA_RECEIVE = 10000
    MODESTR = 'CONSISTANT_SERIAL'
    
    START_SYM = 0x01
    STOP_SYM = 0x3E
    SEPARATE_SYM = 0x3A

    TYPE_SYM = 0x54
    ID_SYM = 0x49
    SENDER_SYM = 0x53
    RECEIVER_SYM = 0x52
    NEXT_SYM = 0x58
    NODE_SYM = 0x4E
    MASK_SYM = 0x7E
    SPACE_SYM = 0x20

    TYPE_BEACON_SYM = 0x30
    TYPE_CONTENT_SYM = 0x31

    def __init__(self, listener, portStr='COM3'):
        try:
            self.conn = serial.Serial(portStr,
                                      115200,
                                      serial.EIGHTBITS,
                                      serial.PARITY_NONE,
                                      serial.STOPBITS_ONE,
                                      timeout=1)
        except:
            raise Exception('Unsuccessful COM Port connection')
        self.listener = listener

    def receive(self):
        while(1):
            self.listener.control()
            if self.conn.in_waiting > 0:
                msg = self.conn.readline()
                if len(msg) > 0:
                    self.listener.receive_callback(msg)
                    

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 19:19:44 2025

@author: krong
"""
import numpy as np
import matplotlib.pyplot as plt
# import pandas as pd
from spyder_kernels.utils.iofuncs import load_dictionary
from rti_gui import choose_file, select_open_folder
from rti_scheme_sideposition import SidePositionScheme
from rti_cal_expdecay import ExpDecayRTICalculator
from rti_sim_input import simulateInput
from rti_estimator import RTIEstimator
from rti_plot import plotRTIIm
from rti_grid import RTIGrid
from rti_eval import convolve2D



def fit_linear_through_origin(x, y):
    """
    Fits the model y = kx and minimizes RMSE.

    Args:
        x (array-like): Practical or observed values.
        y (array-like): Reference or true values.

    Returns:
        k (float): Best-fit scalar multiplier.
        rmse (float): Root Mean Square Error of the fit.
    """
    x = np.array(x)
    y = np.array(y)

    # Compute optimal k
    numerator = np.sum(x * y)
    denominator = np.sum(x * x)
    k = numerator / denominator

    # Predicted values
    y_pred = k * x

    # Compute RMSE
    rmse = np.sqrt(np.mean((y - y_pred) ** 2))

    return k, rmse

def fit_linear_with_intercept(x, y):
    """
    Fits the model y = kx + c and minimizes RMSE.

    Args:
        x (array-like): Practical or observed values.
        y (array-like): Reference or true values.

    Returns:
        k (float): Best-fit slope.
        c (float): Best-fit intercept.
        rmse (float): Root Mean Square Error of the fit.
    """
    x = np.array(x)
    y = np.array(y)

    # Fit using least squares: y = kx + c
    A = np.vstack([x, np.ones(len(x))]).T
    k, c = np.linalg.lstsq(A, y, rcond=None)[0]

    # Predicted values
    y_pred = k * x + c

    # RMSE
    rmse = np.sqrt(np.mean((y - y_pred) ** 2))

    return k, c, rmse

f = choose_file()
atten_set = load_dictionary(f)[0]['l']

att = np.array(atten_set)
avg_att_pos = np.mean(att, axis=0)
v = np.zeros([12,6])

for i in range(12):
    for j in range(6):
        v[i][j] = np.std(att[:, i, j])
        
cv = v/avg_att_pos

sch = SidePositionScheme(area_width=4.,
                         area_length=7.,
                         vx_width=0.2,
                         vx_length=0.2,
                         wa_width=4.,
                         wa_length=7.,
                         n_sensor=12)

cal = ExpDecayRTICalculator(sch)
est = RTIEstimator(cal)

pos_r1 = [1, 2, 3]
pos_r2 = [1.16, 3.5, 5.84]
poS = [(a,b) for b in pos_r2 for a in pos_r1]
# poS = reference_object_position((sch.coordX, sch.coordY), pos_ref, obj_dim=(1, 1))
inp = [simulateInput(sch, cal, pos, obj_dim=(0.4,0.4)) for pos in poS]
out = {}
save = select_open_folder('', title='Choose folder to save')
for i, vl in enumerate(inp):
    for k,v in vl.items():
        
        iM = est.calVoxelAtten(v[0], False)
        out[k] = (v[0], iM)
        # kw = {
        #     'path':save,
        #     'save':save,
        #     'filename':sch.getTitle(fn=True)+k,
        #     'title':sch.getTitle(fn=True)+k,
        #     'label':'Rel. Attenuation',
        #     'atten_range':[np.percentile(iM, 20),np.percentile(iM, 100)]
        #     }
        # plotRTIIm(sch, iM, **kw)

att_pair_pos = {}
RMSE_Link = {}
for h, (ky, val) in enumerate(out.items()):
    att_pair_pos[ky] = []
    for i in range(6):
        idx_r = 2*i+1
        for j in range(6):
             att_pair_pos[ky].append([val[0][6*i+j],att[h][idx_r][j]])
             try: RMSE_Link[f'L{i}{j}'] += (val[0][6*i+j] - att[h][idx_r][j])*(val[0][6*i+j] - att[h][idx_r][j])
             except (NameError, KeyError): 
                 RMSE_Link[f'L{i}{j}'] = 0
                 RMSE_Link[f'L{i}{j}'] += (val[0][6*i+j] - att[h][idx_r][j])*(val[0][6*i+j] - att[h][idx_r][j])
for ky, val in RMSE_Link.items(): RMSE_Link[ky] = np.sqrt(val/36)
att_pair=np.array([vl for k,vl in att_pair_pos.items()])
att_pair_mod = att_pair
iS = []
for h, ll in enumerate(att_pair):
    r_ll, o_ll = ll[:, 0], ll[:,1]
    # o_ll = np.abs(o_ll)
    # k,c,rmse = fit_linear_with_intercept(r_ll.flatten(), o_ll.flatten())
    # att_pair_mod[h,:,1] = k*o_ll+c
    im_r = est.calVoxelAtten(r_ll, False)
    im_o = est.calVoxelAtten(o_ll, False)
    im_rr = ((im_r - np.average(im_r))/np.std(im_r))
    im_oo = ((im_o - np.average(im_o))/np.std(im_o))
    im_rf = RTIGrid.reshapeVoxelM2Arr(im_rr)
    im_of = RTIGrid.reshapeVoxelM2Arr(im_oo)
    k, c, rmse = fit_linear_with_intercept(im_of, im_rf)
    # im_rr = (((im_r - np.average(im_r))/np.std(im_r))+np.average(im_o))*np.std(im_o)
    iS.append([k, c, rmse])
    im_oo = k*im_oo + c
    kw = {
        'path':save,
        'save':save,
        'filename':sch.getTitle(fn=True)+f'P{h}-REF',
        'title':sch.getTitle(fn=True)+f'P{h}-REF',#  y={k:.2f}x',
        'label':'Rel. Attenuation',
        'atten_range':[np.percentile(im_rr, 20),np.percentile(im_rr, 100)]
    }
    # plotRTIIm(sch, im_rr, **kw)
    att_pair_mod[h,:,0] = cal.calIdealLinkAtten(RTIGrid.reshapeVoxelM2Arr(im_rr))
    att_pair_mod[h,:,1] = cal.calIdealLinkAtten(RTIGrid.reshapeVoxelM2Arr(im_oo))
    kw = {
        'path':save,
        'save':save,
        'filename':sch.getTitle(fn=True)+f'P{h}-OBS',
        'title':sch.getTitle(fn=True)+f'P{h}-OBS',
        'label':'Rel. Attenuation',
        'atten_range':[np.percentile(im_o, 20),np.percentile(im_o, 100)]
    }
    # plotRTIIm(sch, im_o, **kw)
    

for h, pair_group in enumerate(att_pair_mod):
    for i, pair in enumerate(pair_group):
        try: RMSE_Link[i] += (pair[1]-pair[0])(pair[1]-pair[0])
        except: RMSE_Link[i] = 0
fV = []
for i in range(36):
    r_att = att_pair_mod[:, i, 0]
    o_att = att_pair_mod[:, i, 1]
   
    k, rmse = fit_linear_through_origin(o_att, r_att)
    fV.append([k, rmse])
    
    n,nei_id = np.unravel_index(i, (6,6))
    r_id = 2*n+1
    s_id = 2*(nei_id + 1)
    # plt.scatter(o_att, r_att, label=f'L{r_id}-{s_id}')
    # plt.plot(o_att, k * np.array(o_att), color='red', label=f'Fit: y = {k:.2f}x')
    # plt.xlabel('Observed Att.')
    # plt.ylabel('Reference Att.')
    # plt.title(f'Variability Fitting RMSE={rmse}')
    # plt.grid()
    # plt.legend()
    # plt.show()
    
    att_pair_mod[:, i, 1] = k*o_att 

results = {}
for h, ll in enumerate(att_pair_mod):
    r_ll, o_ll = ll[:, 0], ll[:,1]
    im_r = est.calVoxelAtten(r_ll, False)
    im_o = est.calVoxelAtten(o_ll, False)
    
    # im_o = ((im_o - np.average(im_o))/np.std(im_o))
    
    RMSE = np.sqrt(np.square(np.subtract(im_r, im_o).mean()))
    LO_Idx = []
    sec_LO = [0, -1e10, 0]
    for hh, vl in enumerate(att_pair_mod):
        im_rr = sch.build_section(hh)#est.calVoxelAtten(vl[:,0], False)
        ri = np.sqrt(np.square(np.subtract(im_rr, im_o)).mean())
        if np.log10(1/ri) > sec_LO[1]: sec_LO[0], sec_LO[1] = hh, np.log10(1/ri)
        sec_LO[2] += np.log10(1/ri)
        
        LO_Idx.append([ri, np.log10(1/ri)])
        
    for hhh, vl in enumerate(LO_Idx):
        vl[1] /= sec_LO[2]
        
    t_pos = sch.find_target(im_o, section=sec_LO[0], pos_mat_dim=(3,3))
    results[h]=(np.array(LO_Idx), sec_LO, t_pos)
    
    # im_rf = im_r.flatten()
    # im_of = im_o.flatten()
    # k, c, rmse = fit_linear_with_intercept(im_rf, im_of)
    # img_pos_scale.append([k,c,rmse])
    # im_rr = k*im_r + c
    # kw = {
    #     'path':save,
    #     'save':save,
    #     'filename':sch.getTitle(fn=True)+f'P{h}-REF',
    #     'title':sch.getTitle(fn=True)+f'P{h}-REF',# y={iS[h][0]:.2f}x+{iS[h][1]:.2f}',
    #     'label':'Rel. Attenuation',
    #     'atten_range':[np.percentile(im_r, 20),np.percentile(im_r, 100)]
    # }
    # plotRTIIm(sch, im_r, **kw)
    # att_pair_mod[h,:,0] = cal.calIdealLinkAtten(im_rr.flatten())
    kw = {
        'path':save,
        'save':save,
        'filename':sch.getTitle(fn=True)+f'P{h+1}-OBS',
        'title':sch.getTitle(fn=True)+f' P{h+1}-RMSE={RMSE:.3f}',
        'label':'Rel. Attenuation',
        'atten_range':[np.percentile(im_o, 20),np.percentile(im_o, 100)]
    }
    plotRTIIm(sch, im_o, **kw)
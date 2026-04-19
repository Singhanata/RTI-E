# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 19:41:27 2025

@author: krong
"""
import os
import numpy as np
import pandas as pd
import glob
from rti_gui import select_open_folder
from rti_plot import plotRTIIm
from rti_scheme_sideposition import SidePositionScheme

def load_matrices_with_prefix(folder_path, prefix, N):
    """Loads the first N matrices from CSV files that match a given prefix."""
    # files = sorted(glob.glob(f"{prefix}*.csv"))[:N]  # Get N matching CSV files (sorted)
    files = sorted(glob.glob(os.path.join(folder_path, f"{prefix}*.csv")))[:N]
    
    if not files:
        raise FileNotFoundError("No matching files found with the given prefix.")
    
    matrices = [pd.read_csv(file, header=None).to_numpy() for file in files]  # Load as NumPy arrays
    
    return matrices, files

def compute_elementwise_average(matrices):
    """Computes element-wise average of a list of matrices."""
    return np.mean(matrices, axis=0)

# def main():
prefix = "img_"  # Change this to match your CSV file prefix
NL = [1,10,100,1000]  # Change this to select how many matrices to include
sch = SidePositionScheme(area_width=4.,
                         area_length=7.,
                         vx_width=0.2,
                         vx_length=0.2,
                         wa_width=4.,
                         wa_length=7.,
                         n_sensor=12)
folder_path = select_open_folder('', title='IMG Open')
save_path = select_open_folder('', title='Choose Record Folder')
img = []
for N in NL:
    try:
        matrices, files = load_matrices_with_prefix(folder_path,prefix, N)
        avg_matrix = compute_elementwise_average(matrices)
        
        # Save the resulting average matrix to a CSV file
        avg_filename = "average_matrix.csv"
        pd.DataFrame(avg_matrix).to_csv(avg_filename, index=False, header=False)
        
        print(f"Average matrix computed from {len(files)} files and saved as '{avg_filename}'")
        print("Files used:", files)
        img.append(avg_matrix)
        kw = {
            'path':save_path,
            'save':save_path,
            'filename':sch.getTitle(fn=True)+f'_N{N}',
            'title':sch.getTitle(fn=True)+f'_N{N}',
            'label':'Rel. Attenuation',
            'atten_range':[np.percentile(avg_matrix, 20),np.percentile(avg_matrix, 100)]
            }
        plotRTIIm(sch, avg_matrix.T, **kw)
        # Optional: Display the average matrix
        # print(avg_matrix)

    except Exception as e:
        print("Error:", e)

# if __name__ == "__main__":
#     main()

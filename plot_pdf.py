# -*- coding: utf-8 -*-
"""
Created on Sun Mar 16 19:51:53 2025

@author: krong
"""

import numpy as np
import scipy.stats as stats
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from rti_gui import select_open_folder
from rti_emulator import read_and_concatenate_csv_files

def analyze_population_with_plot(population_2d, NID=0, separate_plots=False, odd=False, title=''):
    """
    Analyzes a 2D population dataset where each row is treated as a separate group.
    Computes statistical values, tests for normality, and plots the PDF for each group.

    Args:
        population_2d (list of lists): 2D list where each row represents a population group.
        separate_plots (bool): If True, plot each group separately, otherwise plot all together.

    Returns:
        DataFrame: Statistical results for each group.
    """
    results = []
    ti=title
    colors = sns.color_palette("tab10", len(population_2d))  # Generate distinct colors for each group
    for i, data in enumerate(population_2d):
        if title == [] and len(population_2d) == 1: ptitle = 'Population'
        else: ptitle = title + f' - {i}'
        if title == 'Link':
            no = 2*i+1
            if (NID & 1): no = 2*(i+1)
            ti = f'NODE {NID}'
            ptitle = f'Link {NID}-{no}'
        if not isinstance(population_2d[0], list): data = population_2d
        # print(data)
        data = np.array(data)  # Convert to NumPy array for numerical operations
        n = len(data)

        # Compute statistics
        mean = np.mean(data)
        std_dev = np.std(data, ddof=1)  # Sample standard deviation (ddof=1)
        sem = std_dev / np.sqrt(n)  # Standard Error of the Mean (SEM)
        ci_95 = stats.t.interval(0.95, df=n-1, loc=mean, scale=sem)  # 95% Confidence Interval

        # Normality Test (Shapiro-Wilk)
        shapiro_stat, shapiro_p = stats.shapiro(data)
        normality = "Normal" if shapiro_p > 0.05 else "Not Normal"  # p > 0.05 means normal

        results.append({
            "POP": ptitle,
            "Mean": mean,
            "Std Dev": std_dev,
            "SEM": sem,
            "95% CI Lower": ci_95[0],
            "95% CI Upper": ci_95[1],
            "Shapiro-Wilk p": shapiro_p,
            "Normality": normality
        })

        # Plot PDF for each group
        if separate_plots:
            plt.figure(figsize=(8, 5))
            sns.kdeplot(data, label=ptitle, fill=True, alpha=0.3, color=colors[i])
            plt.axvline(mean, color=colors[i], linestyle='dashed', linewidth=2)
            plt.text(mean, plt.ylim()[1] * 0.95, f'Mean ({mean:.2f})', color=colors[i], ha='center')
            plt.xlabel("Value")
            plt.ylabel("Density")
            plt.title("Probability Density Function (PDF) - " + ptitle)
            # plt.legend()
            plt.grid()
            plt.show()
        if not isinstance(population_2d[0], list): break

    # If not separate_plots, plot all groups together
    if not separate_plots:
        plt.figure(figsize=(10, 6))
        for i, data in enumerate(population_2d):
            n = 2*i+1
            if NID&1: n = 2*(i+1)
            if not isinstance(data, list): data=population_2d
            sns.kdeplot(data, label=ptitle, fill=True, alpha=0.3, color=colors[i])
            plt.axvline(results[i]['Mean'], color=colors[i], linestyle='dashed', linewidth=2)
            plt.text(results[i]['Mean'], plt.ylim()[1] * 0.95, f'Mean ({results[i]['Mean']:.2f})', color=colors[i], ha='center')
            if not isinstance(data[0], list):break
        plt.xlabel("Value")
        plt.ylabel("Density")
        plt.title("Probability Density Function (PDF) of "+ ti)
        if i > 0: plt.legend()
        plt.grid()
        plt.show()
        

    # Convert results to DataFrame
    df_results = pd.DataFrame(results)

    return df_results

def convert_1D_to_3D(lst, depth, rows, cols):
    # Ensure the list has the correct length, otherwise pad with None or 0
    total_elements = depth * rows * cols
    if len(lst) < total_elements:
        lst += [None] * (total_elements - len(lst))  # Padding
    
    # Convert to 3D list
    return [
        [lst[i + j * cols : i + (j + 1) * cols] for j in range(rows)]
        for i in range(0, total_elements, rows * cols)]

# Example Usage
population_data = [
    [1.2, 2.3, 2.1, 1.8, 2.0],  # Group 1
    [5.1, 5.3, 5.2, 5.4, 5.5],  # Group 2
    [10.1, 10.3, 10.2, 10.4, 10.5]  # Group 3
]

if __name__ == '__main__':
    p = select_open_folder('')
    data = read_and_concatenate_csv_files(p, 'N1rssi')
    
    # Call the function with separate_plots=True to get individual plots
    res = analyze_population_with_plot(data, NID=1, separate_plots=True, title='Link')

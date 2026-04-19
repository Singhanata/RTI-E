import numpy as np
import scipy.stats as stats
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from rti_gui import select_open_folder
from rti_emulator import read_and_concatenate_csv_files
from plot_pdf import analyze_population_with_plot

 
def compare_rssi_means(before_rssi, after_rssi, title='Group'):
    """
    Compares the mean RSSI values before and after obstruction.
    
    Args:
        before_rssi (list): RSSI values before obstruction.
        after_rssi (list): RSSI values after obstruction.
    
    Returns:
        DataFrame: Statistical comparison results.
    """
    before_rssi = np.array(before_rssi)
    after_rssi = np.array(after_rssi)

    # Compute statistics
    mean_before, std_before, n_before = np.mean(before_rssi), np.std(before_rssi, ddof=1), len(before_rssi)
    mean_after, std_after, n_after = np.mean(after_rssi), np.std(after_rssi, ddof=1), len(after_rssi)

    # Compute confidence intervals for each mean
    ci_95_before = stats.t.interval(0.95, df=n_before-1, loc=mean_before, scale=std_before/np.sqrt(n_before))
    ci_95_after = stats.t.interval(0.95, df=n_after-1, loc=mean_after, scale=std_after/np.sqrt(n_after))

    # Compute difference of means
    mean_diff = mean_after - mean_before
    
    # Compute standard error of the difference
    se_before = std_before / np.sqrt(n_before)
    se_after = std_after / np.sqrt(n_after)
    se_diff = np.sqrt(se_before**2 + se_after**2)

    # Confidence Intervals (95% CI) for mean difference
    df = ((se_before**2 + se_after**2) ** 2) / (
        ((se_before**2) ** 2) / (n_before - 1) + ((se_after**2) ** 2) / (n_after - 1)
    )
    t_crit = stats.t.ppf(0.975, df)  # 95% CI critical value
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff

    # Perform Independent t-test (Welch's test)
    t_stat, p_value = stats.ttest_ind(before_rssi, after_rssi, equal_var=False)
    significance = "Significant Difference" if p_value < 0.05 else "No Significant Difference"

    # Store results in DataFrame
    results = pd.DataFrame({
        "Group": [title + " Before Obstruction", title + " After Obstruction", title + " Mean Difference"],
        "Mean RSSI": [mean_before, mean_after, mean_diff],
        "Std Dev": [std_before, std_after, "-"],
        "Std Error": [se_before, se_after, se_diff],
        "95% CI Lower": [ci_95_before[0], ci_95_after[0], ci_lower],
        "95% CI Upper": [ci_95_before[1], ci_95_after[1], ci_upper]
    })

    comparison_result = pd.DataFrame([{
        "Test Type": "Independent t-test (Welch's test)",
        "T-Statistic": t_stat,
        "P-Value": p_value,
        "Significance": significance
    }])

    # Print results
    print("\n📊 RSSI Statistics:\n", results.to_string(index=False))
    print("\n📊 Comparison Results:\n", comparison_result.to_string(index=False))

    # Create PDF Plot
    plt.figure(figsize=(10, 6))
    sns.kdeplot(before_rssi, label=title + " Before Obstruction", fill=True)
    sns.kdeplot(after_rssi, label=title + " After Obstruction", fill=True)
    
    # Draw vertical lines for means
    plt.axvline(mean_before, color='blue', linestyle='dashed', linewidth=2)
    plt.axvline(mean_after, color='red', linestyle='dashed', linewidth=2)
    
    # Add text annotations for means
    plt.text(mean_before, plt.ylim()[1] * 0.95, f'Mean: {mean_before:.2f}', color='blue', ha='center')
    plt.text(mean_after, plt.ylim()[1] * 0.85, f'Mean: {mean_after:.2f}', color='red', ha='center')
    
    # Add horizontal lines for standard deviations (sigma)
    # plt.hlines(y=plt.ylim()[1] * 0.1, xmin=mean_before - std_before, xmax=mean_before + std_before, color='blue', linestyle='solid', linewidth=2, label=f'Sigma Before')
    # plt.hlines(y=plt.ylim()[1] * 0.15, xmin=mean_after - std_after, xmax=mean_after + std_after, color='red', linestyle='solid', linewidth=2, label=f'Sigma After')
    
    plt.xlabel("RSSI Value")
    plt.ylabel("Density")
    plt.title(title + " RSSI Distribution Before and After Obstruction")
    plt.legend()
    plt.grid()
    plt.show()

    return results, comparison_result

def mean_difference_with_ci(mean_before, std_before, n_before, mean_after, std_after, n_after, confidence=0.95):
    """
    Computes the difference between two means along with the confidence interval.

    Args:
        mean_before (float): Mean before obstruction.
        std_before (float): Standard deviation before obstruction.
        n_before (int): Sample size before obstruction.
        mean_after (float): Mean after obstruction.
        std_after (float): Standard deviation after obstruction.
        n_after (int): Sample size after obstruction.
        confidence (float): Confidence level (default: 0.95 for 95% CI).

    Returns:
        tuple: (Difference of means, Lower CI bound, Upper CI bound)
    """
    # Compute difference of means
    mean_diff = mean_after - mean_before

    # Compute standard error of the difference
    se_before = std_before / np.sqrt(n_before)
    se_after = std_after / np.sqrt(n_after)
    se_diff = np.sqrt(se_before**2 + se_after**2)

    # Degrees of freedom (Welch-Satterthwaite equation)
    df = ((se_before**2 + se_after**2) ** 2) / (
        ((se_before**2) ** 2) / (n_before - 1) + ((se_after**2) ** 2) / (n_after - 1)
    )

    # t-critical value for confidence interval
    t_crit = stats.t.ppf((1 + confidence) / 2.0, df)

    # Compute confidence interval
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff

    return mean_diff, ci_lower, ci_upper

# Example Data
# mean_before = -50
# std_before = 2
# n_before = 1000

# mean_after = -60
# std_after = 2
# n_after = 1000

# # Compute mean difference and CI
# diff, ci_lower, ci_upper = mean_difference_with_ci(mean_before, std_before, n_before, mean_after, std_after, n_after)

# Print results
# print(f"Difference of Means: {diff:.2f}")
# print(f"95% Confidence Interval: ({ci_lower:.2f}, {ci_upper:.2f})")
if __name__ == '__main__':
    spMean, ciLow, ciUpp, std_b, std_a = [], [], [], [], []
    res_all, com_all = {}, {}
    r = select_open_folder('', title = 'REF')
    for j in range(1,10,1):
        p = select_open_folder('', title = 'TARGET')
        
        for nd in range(1,13,1):
            dr = read_and_concatenate_csv_files(r, f'N{nd}rssi')
            dp = read_and_concatenate_csv_files(p, f'N{nd}rssi')
            i=0
            res, com_res = {}, {}
            for (row1, row2) in zip(dr, dp):
                n = 2*i+1
                if nd & 1:2*(i+1)
                ti = f'Link {nd}-{n}'
                k = f'L{nd}-{n}'
                
                res[k], com_res[k] = compare_rssi_means(row1, row2, title=ti)
                spMean.append(res[k]['Mean RSSI'][2])
                ciLow.append(res[k]['95% CI Lower'][2])
                ciUpp.append(res[k]['95% CI Upper'][2])
                std_b.append(res[k]['Std Dev'][0])
                std_a.append(res[k]['Std Dev'][1])
                i += 1
        res_all[j] = res
        com_all[j] = com_res
            
    res_pdf = analyze_population_with_plot(spMean, title='Shadowing Attenuation')
    min_ci = min(ciLow)
    max_ci = max(ciUpp)
# Example Usage
# before_rssi_samples = np.random.normal(-50, 2, 1000)  # RSSI before obstruction
# after_rssi_samples = np.random.normal(-60, 2, 1000)   # RSSI after obstruction
# 
# compare_rssi_means(before_rssi_samples, after_rssi_samples)
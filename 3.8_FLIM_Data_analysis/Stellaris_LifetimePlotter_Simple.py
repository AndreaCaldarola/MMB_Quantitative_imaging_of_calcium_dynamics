# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 15:12:35 2025

By Sebastian Palacios Martinez
"""

# This is a modified version of a custom script for plotting fit lifetime data from LASX. 
# It requires as input a .csv file with lifetime data per cell/frame as individual rows.
# The columns 'Name', 'Time', 'Region', 'Mean τ, Intensity Weighted  ns', 'Mean τ, Amplitude Weighted ns', 'χ²' should be present.
# Set work directory, filename and wether to plot intensity or amplitude lifetime on lines 23, 26 and 29, respectively.

#import libraries
import pandas as pd
import os
import matplotlib.pyplot as plt
from cycler import cycler




#### Set folder where data is located ####
data_folder = 'C:/Users/spalaci/OneDrive - UvA/PhD/Data analysis/250620_HUVEC_FLITSnano_comparison/260211_3-comp_fit/'
os.chdir(data_folder)

#### Set filename to import and to use as plot title ####
filename = 'TL2_3componentFit.csv'

#### Chose which lifetime weight to plot between int and amp ####
lifetime = 'amp'





#Get only the necessary data columns from the file
columns_to_keep = ['Name', 'Time', 'Region', 'Mean τ, Intensity Weighted  ns', 'Mean τ, Amplitude Weighted ns', 'χ²']

#create a new data frame with the selected columns, index by ROI ('Region' column)
df = pd.read_csv(data_folder + filename , usecols=columns_to_keep, index_col='Region')

#Remove overall Decay if it's present
df = df[df.index != 'Overall Decay']

# Replace 'ROI' with 'Cell' in the index
df.index = df.index.str.replace('ROI', 'Cell', regex=False)

#Fix double space between in "Intensity Weighted  ns"
df = df.rename(columns={'Mean τ, Intensity Weighted  ns': 'Mean τ, Intensity Weighted ns'})

print(df.head)


#Create new column at the end of data frame that copies the unique values from time column and converts them from string to float.
df['TimeFixed2'] = None
df['TimeFixed2'] = df['Time'].str[:-2].astype(float)

print(df.loc[:,'TimeFixed2'])



if lifetime == 'amp':
    pvar = 'Amplitude'
    #Calculate Mean Amplitude weighted lifetime per time
    mean_per_time = df.groupby('TimeFixed2')['Mean τ, Amplitude Weighted ns'].mean().reset_index()
elif lifetime == 'int':
    pvar = "Intensity"
    #Calculate Mean Intensity weighted lifetime per time
    mean_per_time = df.groupby('TimeFixed2')['Mean τ, Intensity Weighted ns'].mean().reset_index()
else:
    print("lifetime weight must be either amp or int")


# --- Outlier detection and removal using IQR method ---
#Threshold between 0.5-1.5 ok for removing data when arm is lifted, if not present leave at 100
def remove_outliers(df, col, group_col='Region', threshold=100):
    """Removes outliers from df[col] grouped by group_col using IQR method."""
    clean_df = pd.DataFrame()
    for region, group in df.groupby(group_col):
        Q1 = group[col].quantile(0.25)
        Q3 = group[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        filtered_group = group[(group[col] >= lower_bound) & (group[col] <= upper_bound)]
        clean_df = pd.concat([clean_df, filtered_group])
    return clean_df

# Apply to your selected variable
target_col = f"Mean τ, {pvar} Weighted ns"
df = remove_outliers(df, target_col)

# Recompute mean per time using clean df
mean_per_time = df.groupby('TimeFixed2')[target_col].mean().reset_index()



#Begin plot

plt.figure(figsize=(7, 4))
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['axes.prop_cycle'] = cycler(color=[
    '#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', 
    '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC'
])



# Group the dataframe by Region and plot each region (Cell) separately
for region, group in df.groupby(df.index):
    # Sort by time just in case
    # group = group.sort_values('TimeFixed2')
    plt.plot(group['TimeFixed2'], group['Mean τ, '+pvar+' Weighted ns'], label=f'{region}', alpha=0.6)

    
 # Calculate and plot overall mean line
plt.plot(mean_per_time['TimeFixed2'], mean_per_time['Mean τ, '+pvar+' Weighted ns'],
         color='black', linewidth=4, linestyle='--', label='Mean')



 #Set range based on intensity or amplitude lifetime
if lifetime == 'amp': 
    plt.ylim(2.0, 4.0)
else:
    plt.ylim(3.0, 4.5)
#plt.xlim(0, 620)
plt.xlabel('Time (s)')
plt.ylabel('Mean τ, '+pvar+' Weighted (ns)')
#plt.title(filename)
plt.title('G-Ca-FLITS')
plt.grid(True)
plt.legend(title='Region', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.axvline(x=20.7, color='grey', linewidth=1.5, linestyle='--')
plt.axvline(x=77, color='grey', linewidth=1.5, linestyle='--')
plt.axvline(x=300, color='grey', linewidth=1.5, linestyle='--')




# --- Add treatment boxes over time ---
def add_treatment_boxes(treatments):
    """
    Draw shaded boxes and labels for treatments.
    treatments: list of dicts with keys:
        'start' (float): start time in seconds
        'end' (float): end time in seconds
        'label' (str): text to show inside the box
        'color' (str): matplotlib color (optional)
        'alpha' (float): transparency between 0–1 (optional)
    """
    for t in treatments:
        color = t.get('color', 'lightgray')
        alpha = t.get('alpha', 0.3)  # default transparency
        plt.axvspan(t['start'], t['end'], color=color, alpha=alpha)
        plt.text(
            (t['start'] + t['end']) / 2,
            plt.ylim()[1] - 0.05 * (plt.ylim()[1] - plt.ylim()[0]),
            t['label'],
            ha='left', va='top',
            fontsize=10,
            color='black',
            fontweight='bold'
        )


# Example: define your treatments here
treatments = [
    {'start': 50, 'end': 615, 'label': 'Histamine 100 μM', 'color': 'lightblue', 'alpha': 0.25},
    #{'start': 380, 'end': 730, 'label': 'F+I', 'color': 'lightblue', 'alpha': 0.5},
]

# Add them to the plot
add_treatment_boxes(treatments)





plt.show()




















#To do's: 
    #Feneralize input/output, do multiple experiments simultaneous (i.e, label all cells individually evenif there are multiple insances of ROI)
    #Write into functions
    
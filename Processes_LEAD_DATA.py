# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 16:43:48 2024

@author: Andrew Jones
"""

import pandas as pd
import os
import numpy as np
os.chdir("J:/My Drive/Data/LEAD Data/")

def make_processsing_folders():
    # List of folder names to check or create
    parent_folder=  "Processed Data"

     # Check and create parent folder
    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)
        print(f"Created folder: {parent_folder}")
    else:
        print(f"Folder already exists: {parent_folder}")

    # Check and create the first sub-folder

make_processsing_folders()  
os.chdir("J:/My Drive/Data/LEAD Data/Raw Data/")

os.listdir()
for file in os.listdir():
    data= pd.read_csv(file, skiprows=range(0,8))
    
    data.iloc[:,5:] = data.iloc[:,5:].replace(['-'], np.nan).astype(float).round(2)
    data.to_csv(f"J:/My Drive/Data/LEAD Data/Processed Data/{file}")

# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 12:21:46 2024

@author: Andrew Jones 
"""
import pandas as pd
import geopandas as gpd 
import seaborn as sns
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt

outage_data = pd.read_csv("C:/Users/andre/Downloads/20230101T070100_20240915T070900_zip_outage_data/20230101T070100_20240915T070900_zip_outage_data.csv")
outage_data["Datetime"] = pd.to_datetime(outage_data["Run Start Time"])
zipcodes = gpd.read_file(
    'C:/Users/andre/OneDrive/Documents/Desktop/Temp_for_PNG/Temp_for_PNG/Data/tl_2023_us_zcta520/tl_2023_us_zcta520.shp')
AZ_zipcodes = gpd.read_file(
    'J:/My Drive/Data/Shapefiles/Arizona_Zip_Codes/Arizona_Zip_Codes.shp')
States = gpd.read_file(
    'C:/Users/andre/OneDrive/Documents/Desktop/Temp_for_PNG/Temp_for_PNG/Data/tl_2023_us_state/tl_2023_us_state.shp')
AZ = States[States.STUSPS== "AZ"]
population_count = pd.read_excel(
"J:/My Drive/Data/DECENNIALDHC2020.P1-2024-12-01T020116.xlsx", sheet_name="Data")

census_place = gpd.read_file(
    "J:/My Drive/Data/Shapefiles/tl_2023_04_place_census_places/tl_2023_04_place.shp")

urban_class = gpd.read_file(
"J:/My Drive/Data/Shapefiles/tl_2009_us_uac00_2000_Urban classification/tl_2009_us_uac00.shp")

AZ_urban = urban_class.clip(AZ, keep_geom_type=True)

#Removes the ZCTA from in front of the zip code
new_columns = population_count.columns.str.lstrip("ZCTA5 ")
population_count.columns =new_columns 

population_count = population_count.melt(id_vars= "Label", var_name = "ZIP", value_name = "POP_DEC2020")

#Joins the population data to the zip-codes
AZ_zipcodes_merged = AZ_zipcodes.set_index("ZIP").join(population_count.set_index("ZIP"), on = "ZIP")

#Classifies zip codes based on population


#DOE defintion of an outage event
outage_data.loc[:,"Outage Event (DOE)"]=0
outage_data.loc[((outage_data["Customers Out"]>=50000)),
                "Outage Event (DOE)"]=1

#Abdelmalak et al., 2023 definition of an outage
outage_data.loc[:,"Outage Event (a_h)"]=0
outage_data.loc[((outage_data["Customers Out"]>=20000)) ,"Outage Event (a_h)"]=1


#My definition definition of an outage (50% of the customers are out )
outage_data.loc[:,"Outage Event (customer_pct)"]=0
outage_data.loc[((outage_data["Percent Out"]>=50)) ,"Outage Event (customer_pct)"]=1



event_data = outage_data.groupby(
    ["Zip Code",outage_data['Datetime'].dt.date]).sum().filter(like="Outage Event")

#Replaces the days where more than 50% of the customers and did not have power for at least 3 hours ((3 hrs/15 minutes))
event_data.mask(event_data>=12,1, inplace= True)


event_data.index.names = ["ZIP", "Datetime"]
event_data.index = event_data.index.set_levels([event_data.index.levels[0].astype(str), 
                               event_data.index.levels[1]])
##This code will no longer work due to there being a multiindex. I also removed the requirement of the rural and urban classification s
#TODO: Confirm with Blaise if this graph looks correct based on his experience
# AZ_zipcodes_merged.POP_DEC2020 = AZ_zipcodes_merged.POP_DEC2020.str.replace(',','').astype('float')
# Urban_areas = AZ_zipcodes_merged.reset_index().overlay(
#     AZ_urban,
#     keep_geom_type = True,
#     how="intersection")["ZIP"]
# Urban_areas = Urban_areas[Urban_areas.duplicated()]
# AZ_zipcodes_merged.plot(column = "U/R", legend = True)

# AZ_zipcodes_merged.loc[
#     AZ_zipcodes_merged.index.isin(Urban_areas),"U/R"]= "U"
# AZ_zipcodes_merged.loc[
#     (~(AZ_zipcodes_merged.index.isin(Urban_areas)) &
#       (AZ_zipcodes_merged.POP_DEC2020<=50000)),"U/R"]= "R"
# AZ_zipcodes_merged.loc[:,"U/R"]= "U"
# urban_zips = outage_data[outage_data["Zip Code"].astype(str).isin(Urban_areas)]
# rural_zips = outage_data[~outage_data["Zip Code"].astype(str).isin(Urban_areas)]
AZ_zipcodes_merged = pd.DataFrame(event_data).join(AZ_zipcodes_merged, on= "ZIP")
# outage_data.loc[((urban_zips.index) & 
#                 (outage_data["Customers Out"]>=50000)) ,"Outage Event (a_h)"]=1



# urban_zips = outage_data[outage_data["Zip Code"].astype(str).isin(Urban_areas)]
# rural_zips = outage_data[~outage_data["Zip Code"].astype(str).isin(Urban_areas)]

# outage_data.loc[((urban_zips.index) & 
#                 (outage_data["Customers Out"]>=50000)) ,"Outage Event (a_h)"]=1

AZ_zipcodes_merged[AZ_zipcodes_merged["Outage Event (a_h)"]>=1].plot(column ="Outage Event (a_h)" )

daily_outage_data = outage_data.groupby([outage_data["Zip Code"],
    outage_data["Datetime"].dt.date]).agg({"Outage Event (a_h)":"max",
                                           "Outage Event (DOE)":"max",
                                           "Outage Event (customer_pct)":"max",                
                                                  "Total Customers":"max"})
                                           
daily_outage_data.reset_index(inplace= True)

daily_outage_data["Zip Code"] = daily_outage_data["Zip Code"].astype(str)
                                              
count_of_outages_per_zip = event_data.groupby("ZIP").sum()

count_of_outages_per_zip_shp = AZ_zipcodes.join(count_of_outages_per_zip, on= "ZIP")
count_of_outages_per_zip_shp.columns = ['OBJECTID_1', 'ZIP', 'PO_NAME', 'STATE', 'GlobalID', 'created_us',
       'created_da', 'last_edite', 'last_edi_1', 'Shape__Are', 'Shape__Len',
       'geometry', 'Outage_DOE', 'Outage_a_h',
       'Outage_cust_pct']

count_of_outages_per_zip_shp.to_file("J:/My Drive/Data/Shapefiles/Outage_data/outage_metric.shp")


# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a script to use the clipped  script file.
"""


# pip install geopandas
# pip install numpy
# pip install matplotlib
# pip install seaborn
# pip install arcpy


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# import geopandas as gpd
plt.rcParams['figure.dpi'] = 1500
AZ_counts_of_disasters = pd.read_csv("J:/My Drive/Data/Cost_of_natural_disasters_AZ.csv")

AZ_counts_of_disasters.Year = AZ_counts_of_disasters.Year.astype(int).astype(str)
melted_data = AZ_counts_of_disasters.melt(id_vars= "Year", var_name = "Type of Disasters", 
                                          value_name = "Count of Events")

g = sns.FacetGrid(data = melted_data, col="Type of Disasters",  col_wrap=3,
                  height=3, aspect=1.15)
g.map(sns.scatterplot, "Year", "Count of Events",size =1.2)
g.map(sns.lineplot, "Year", "Count of Events",linewidth = 0.8 )
plt.xticks(rotation=45)
g.tight_layout()
g.savefig("J:/My Drive/Figures/Natural_disasters_count.png")




AZ_cost_of_disasters = pd.read_csv("J:/My Drive/Data/Cost_of_natural_disasters_AZ.csv")
cost_cols = AZ_cost_of_disasters.filter(like= "Cost")
Year = AZ_cost_of_disasters["Year"]
cost_cols_names = ['Drought Cost Range', 'Flooding Cost Range', 
       'Severe Storm Cost Range', 
       'Wildfire Cost Range', 
       'All Disasters Cost Range']
cost_cols = cost_cols.loc[:,cost_cols_names]
combined_cost_data = pd.DataFrame()
for i in cost_cols.columns:
    lower_bound_cost  = AZ_cost_of_disasters.loc[:,i].str.split("-").str[0]
    upper_bound_cost = AZ_cost_of_disasters.loc[:,i].str.split("-").str[1]
    diaster = i
    
    data_cost = pd.DataFrame(data = {"lower_bound_cost":lower_bound_cost.values,
                                     "upper_bound_cost":upper_bound_cost.values,
                                     "disasters":i},
                             index =Year )
    data_cost_melt = data_cost.melt(id_vars = "disasters", var_name = "Cost_type", value_name = "Cost", 
                                    ignore_index = False)
    combined_cost_data = pd.concat([combined_cost_data,data_cost],
              ignore_index=False,
              axis =0)

# combined_cost_data_panel_data = combined_cost_data.reset_index().set_index(["disasters","Year"])


combined_cost_data.lower_bound_cost = combined_cost_data.lower_bound_cost.astype(float)
combined_cost_data.upper_bound_cost = combined_cost_data.upper_bound_cost.astype(float)

combined_cost_data_panel_data = combined_cost_data.groupby(["disasters", "Year"]).mean()

combined_cost_data_panel_data.loc[:,"Median_cost"] = combined_cost_data_panel_data.median(axis=1)
combined_cost_data_panel_data = combined_cost_data_panel_data.div(100)

combined_cost_data_panel_data.loc[:,"Decade"] = np.floor(combined_cost_data_panel_data.index.get_level_values("Year")/10)*10
average = combined_cost_data_panel_data.groupby(["disasters","Decade"]).mean()
plotting_data = average.melt(ignore_index= False).reset_index()

fig,axs = plt.subplots(constrained_layout = True)
sns.lineplot(ax=axs, data = plotting_data, x="Decade",
             y ="value", hue = "disasters", legend= False   )
sns.scatterplot(ax=axs,data = plotting_data[plotting_data.variable == "Median_cost"], x="Decade",
             y ="value", hue = "disasters", style="disasters", s=40   )
axs.set_ylabel("Billion Dollars loss")
axs.legend(frameon=False)
sns.despine(ax=axs)
plt.savefig("J:/My Drive/Figures/Natural_disasters_cost.svg",dpi= 1500 )
average.to_csv("J:/My Drive/Data/Natural_disasters_proceeded_data.csv")



sns.boxplot(data = combined_cost_data_panel_data.reset_index(),
            x= "upper_bound_cost",
            y = "disasters")




fig,axs= plt.subplots(2,3,figsize=(9,5),sharey= True,
                     constrained_layout= True)
axs= axs.ravel()
for i,dis_name in enumerate(cost_cols.columns):
    focus_data = combined_cost_data_panel_data[
        combined_cost_data_panel_data.index.get_level_values(level=0) == dis_name].reset_index()
    y_error_min = np.array(focus_data["lower_bound_cost"].replace(0,np.nan))
    y_error_max = np.array(focus_data["upper_bound_cost"].replace(0,np.nan))
    y_error  =[y_error_min,y_error_max]
    sns.lineplot(
                ax=axs[i],
                data = focus_data,
                color="green",
                x = "Year",
                linewidth =1.4 ,
                y = "Median_cost", 
                zorder =1)
    axs[i].errorbar(
        data = focus_data,
        color="black",
        # fmt ='o',
        capsize= 4,
        # markersize = 2, 
        capthick = 0.1,
        x = "Year",
        y = "Median_cost",
        zorder = 0,
        yerr= y_error)
    sns.scatterplot(
                ax=axs[i],
                data = focus_data,
                color="darkgreen",
                s = 9, 
                x = "Year",
                y = "Median_cost", 
                zorder= 2)
    # sns.lineplot(
    #             # ax=axs[i],
    #             color="darkgreen",
    #             marker=["O"],
    #             data = focus_data,
    #             x = "Year",
    #             y = "Median_cost")
    # axs[i].fill_between(
    #     focus_data.Year,
    #     focus_data.upper_bound_cost,
    #     focus_data.lower_bound_cost,
    #     alpha = 0.4, color= "gray")
    axs[i].set_title(dis_name, fontsize=12)
    sns.despine(ax=axs[i])
    axs[i].set_ylabel("Cost [Billion USD]*")

g = sns.FacetGrid(data = combined_cost_data_panel_data.reset_index(), 
                  col="disasters",  col_wrap=3,
                  height=3, aspect=1.15)
g.map(sns.scatterplot, "Year", "Median_cost",size =1.2)
g.map(sns.lineplot, "Year", "Median_cost",linewidth = 0.8 )
plt.fill_between(x, upper, lower, alpha=0.2)
g.tight_layout()

EIA_reporting_reliability_data = pd.read_excel(
    "J:/My Drive/Data/Reliability_EIA_2023_2013.xlsx",
    sheet_name="Combined_data",header=[2])
EIA_reporting_reliability_data.replace('.',np.nan, inplace= True)

order_CAIDI_with_major_event= EIA_reporting_reliability_data.groupby("Utility Name")[
    "CAIDI (minutes per interruption) (ME)"].median().sort_values(ascending= False).index.values


fig,axs = plt.subplots(2,1, figsize = (9,5),
                       constrained_layout = True, 
                       sharey=True)
sns.boxplot(ax=axs[0],
            data = EIA_reporting_reliability_data, 
            y = "Utility Name",
            x = "CAIDI (minutes per interruption) (ME)", 
            order=order_CAIDI_with_major_event ,
            linewidth=2.5)
# axs[0].axvline(EIA_reporting_reliability_data.groupby("Utility Name")[
#     "CAIDI (minutes per interruption)"].median().median())
# axs[0].axvline(2*EIA_reporting_reliability_data.groupby("Utility Name")[
#     "CAIDI (minutes per interruption)"].median().median(), 
#     color = "red")
sns.boxplot(ax=axs[1],
            data = EIA_reporting_reliability_data, 
            y = "Utility Name",
            x = "CAIDI (minutes per interruption)(W/O ME)", 
            order=order_CAIDI_with_major_event)
axs[1].axvline(2*EIA_reporting_reliability_data.groupby("Utility Name")[
    "CAIDI (minutes per interruption)"].median().median(), 
    color = "red")
for i in range(2):
    axs[i].set_xlim(0,400)
sns.despine(ax=axs)





fig,axs = plt.subplots(5,3,figsize= (10,11),
                       constrained_layout = True)
axs=axs.ravel()
for id_num, utility in enumerate(EIA_reporting_reliability_data["Utility Name"].unique()) :
    data_for_graph = EIA_reporting_reliability_data[
        EIA_reporting_reliability_data["Utility Name"] ==utility][[
            'Data Year', 
            'Utility Name',
            "CAIDI (minutes per interruption) (ME)",
            "CAIDI (minutes per interruption)(W/O ME)"]].melt(
                id_vars =['Data Year', 
                'Utility Name'])
    
    sns.kdeplot(
        ax=axs[id_num],
                data = data_for_graph, fill= True, 
                x = "value",
                hue = "variable",
                color= {
                    "CAIDI (minutes per interruption) ((W/O ME)":"blue",
                    "CAIDI (minutes per interruption)(ME)":"orange"},
            legend= False)
    axs[id_num].set_title(utility, fontsize = 13)
    sns.despine(ax=axs[id_num])
    axs[id_num].axvline(data_for_graph[
        data_for_graph.variable =="CAIDI (minutes per interruption) ((W/O ME)"].median()["value"], 
        color = "blue")
    axs[id_num].axvline(data_for_graph[
        data_for_graph.variable =="CAIDI (minutes per interruption) (ME)"].median()["value"], 
        color = "orange")                           
                              
fig.savefig("J:/My Drive/Figures/Utility_CAIDI.png",dpi= 1500 )



fig,axs = plt.subplots(5,3,figsize= (10,11),
                       constrained_layout = True)
axs=axs.ravel()
for id_num, utility in enumerate(EIA_reporting_reliability_data["Utility Name"].unique()) :
    data_for_graph = EIA_reporting_reliability_data[
        EIA_reporting_reliability_data["Utility Name"] ==utility][[
            'Data Year', 
            'Utility Name',
            "SAIDI (minutes per year) (W/O ME)",
            "SAIDI (minutes per year) (ME)",
                ]].melt(
                id_vars =['Data Year', 
                'Utility Name'] )
    
    sns.kdeplot(
        ax=axs[id_num],
                data = data_for_graph, fill= True, 
                x = "value",
                hue = "variable", 
                color= {
                    "SAIDI (minutes per year) (W/O ME)":"blue",
                    "SAIDI (minutes per year) (ME)":"orange"},
                    legend = True)
    axs[id_num].set_title(utility, fontsize = 13)
    axs[id_num].set_ylabel("")
    axs[id_num].set_xlabel("")
    axs[id_num].axvline(data_for_graph[
        data_for_graph.variable =="SAIDI (minutes per year) (W/O ME)"].median(skipna=True)["value"], 
        color = "blue", ls = "--")
    axs[id_num].axvline(data_for_graph[
        data_for_graph.variable =="SAIDI (minutes per year) (ME)"].median()["value"], 
        color = "orange",ls = "--")     

    if id_num !=14:
      axs[id_num].legend([], frameon=False) 

sns.despine(fig=fig) 
axs[id_num].legend(bbox_to_anchor=(0.5, -0.05), loc='lower center')
fig.supylabel("Density")
fig.supxlabel("Minutes of electric interruption the average customer experiences", 
              fontsize=14)

fig.savefig("J:/My Drive/Figures/Utility_SAIFI.png",dpi= 1500 )

#----------------------------------------------------
#Bar Plot of the gra

# Plotting setup
fig, axs = plt.subplots(5, 3, figsize=(14, 12.5),sharey= True,
                        constrained_layout=True)
axs = axs.ravel()

# Unique utilities
utilities = EIA_reporting_reliability_data["Utility Name"].unique()

for id_num, utility in enumerate(utilities):
    data_for_graph = EIA_reporting_reliability_data[EIA_reporting_reliability_data["Utility Name"] == utility].melt(
        id_vars=['Data Year', 'Utility Name'], 
        value_vars=["SAIDI (minutes per year) (W/O ME)", "SAIDI (minutes per year) (ME)"]
    )
    data_for_graph.variable.replace({
        "SAIDI (minutes per year) (W/O ME)":"No Major Event",
        "SAIDI (minutes per year) (ME)": "With Major Event"}, inplace= True)
    sns.barplot(
        ax=axs[id_num],
        data=data_for_graph, 
        x="value", 
        y = "variable",
        err_kws={'linewidth': 1.5},
        capsize=.2,
        
       hue="variable", 
        palette={
            "No Major Event": "lightblue",
            "With Major Event": "orange"
        }    )

    axs[id_num].set_title(utility, fontsize=14, weight= "bold")
    axs[id_num].set_ylabel("")
    axs[id_num].set_xlabel("")


# Suplabels
fig.supylabel("SAIDI",
              fontsize=20)
fig.supxlabel("Minutes of electric interruption the average customer experiences",
              fontsize=20)

# Clean up plot appearance
sns.despine(fig=fig)
plt.show()


fig.savefig("J:/My Drive/Figures/Utility_SAIFI_bar.png",dpi= 1500 )


fig,axs = plt.subplots(5,3,figsize= (10,11),
                       constrained_layout = True)
axs=axs.ravel()
for id_num, utility in enumerate(EIA_reporting_reliability_data["Utility Name"].unique()) :
    data_for_graph = EIA_reporting_reliability_data[
        EIA_reporting_reliability_data["Utility Name"] ==utility][[
            'Data Year', 
            'Utility Name',
            "SAIDI (minutes per year) (W/O ME)",
            "SAIDI (minutes per year) (ME)",
                ]].melt(
                id_vars =['Data Year', 
                'Utility Name'] )
    
    sns.ecdfplot(
        ax=axs[id_num],
                data = data_for_graph,  
                x = "value",stat = 'count'
                hue = "variable", legend = True)
    axs[id_num].set_title(utility, fontsize = 13)
    axs[id_num].set_ylabel("")
    axs[id_num].set_xlabel("")
    axs[id_num].legend()
    if id_num !=14:
      axs[id_num].legend([], frameon=False) 

sns.despine(fig= fig) 
# fig.legend(handles, labels, bbox_to_anchor=(0.5, -0.05))
fig.supylabel("Counts")
fig.supxlabel("Minutes of electric interruption the average customer experiences", 
              fontsize=14)

fig.savefig("J:/My Drive/Figures/Utility_SAIFI.png",dpi= 1500 )
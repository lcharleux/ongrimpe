# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Analyseur d'entrainement de grimpe
#------------------------------------------------------------------------------- 


#------------------------------------------------------------------------------- 
# PACKAGES
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import weclimb
plt.style.use('ggplot')
#------------------------------------------------------------------------------- 



#------------------------------------------------------------------------------- 
# GETTING DATA FROM GOOGLE DOCS AND PREPROCESSING
googlepath = "https://docs.google.com/spreadsheets/d/1fu1ozajGPJdQnta2Ex3NUbRIV6DadZis0iLIc0Yh0b4/pub?output=csv"
data = weclimb.preprocess(googlepath)   
#-------------------------------------------------------------------------------


  
#-------------------------------------------------------------------------------
# DIRECTORIES
outputdir = "outputs"
if os.path.isdir(outputdir) == False: os.mkdir(outputdir)


#-------------------------------------------------------------------------------
# PROCESSING DATA
groups = data.groupby("climber")
if True:
  climber = "Ludovic"
  group = groups.get_group(climber) 
  print(climber)
  cpath = climber.replace(" ", "_")
  path = "{0}/{1}".format(outputdir, cpath)
  if os.path.isdir(path) == False: os.mkdir(path)
  #weclimb.plot_level_evolution_bouldering(group)
  # Level evolution
  group = pd.concat([group.loc[group.state == "onsight"], 
                     group.loc[group.state == "flash"],
                     group.loc[group.state == "redpoint"],
                    ])
  group = group.loc[group.site == "Cortigrimpe"]                  
  out = group.groupby(["date", "grade"]).agg(
        {"factor": np.sum})
  out = out.unstack().fillna(0)
  plt.figure()
  out.factor.plot(kind = "barh")
  plt.tight_layout()
  plt.savefig("test.pdf")

""" 
for session in sessions:
  for climber in data[data.Date == session].Grimpeur.unique():
    weclimb.plot_difficulty_state_repartition(data, session, climber)

for climber in climbers:
    weclimb.plot_level_evolution_bouldering(data, climber)
    weclimb.plot_level_evolution_sportclimbing(data, climber)
"""    

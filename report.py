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
data = pd.read_csv(googlepath)
data.columns = [k.replace("\n", "") for k in data.keys()] 
data = data.applymap(weclimb.removeLineBreaks)
data.Multiplicateur.fillna(1)
# Processing dates
def processDates(v):
  return "{1}/{0}/{2}".format(*v.split("/"))
data.Date = pd.to_datetime(data.Date.map(processDates))  
#-------------------------------------------------------------------------------

"""
  
#-------------------------------------------------------------------------------
# DIRECTORIES
outputdir = "outputs"
if os.path.isdir(outputdir) == False: os.mkdir(outputdir)

#-------------------------------------------------------------------------------
# PROCESSING DATA
climbers = data.Grimpeur.unique() # List of registered climbers
for climber in climbers:
  cpath = climber.replace(" ", "_")
  path = "{0}/{1}".format(outputdir, cpath)
  if os.path.isdir(path) == False: os.mkdir(path)
  
walls = data.Salle.unique()       # List of registers walls
sessions = data.Date.unique()
"""

""" 
for session in sessions:
  for climber in data[data.Date == session].Grimpeur.unique():
    weclimb.plot_difficulty_state_repartition(data, session, climber)

for climber in climbers:
    weclimb.plot_level_evolution_bouldering(data, climber)
    weclimb.plot_level_evolution_sportclimbing(data, climber)
"""    

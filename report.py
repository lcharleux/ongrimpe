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
site_map = {"Cortigrimpe": "boulder",
            "Glaisins": "route"}
data = weclimb.preprocess(googlepath, site_map)   
#-------------------------------------------------------------------------------


  
#-------------------------------------------------------------------------------
# DIRECTORIES
outputdir = "outputs"
if os.path.isdir(outputdir) == False: os.mkdir(outputdir)
if os.path.isdir(outputdir+"/global") == False: os.mkdir(outputdir+"/global")


#-------------------------------------------------------------------------------
# PROCESSING DATA
output = pd.concat([ weclimb.boulder_intensity(data = data),
                     weclimb.boulder_volume(data = data)], axis = 1)

output2 = pd.concat([ weclimb.route_intensity(data = data)])
                     
#-------------------------------------------------------------------------------
# AND PLOT !    

# BOULDERING
fig, axarr = plt.subplots(2, figsize=(7,7), sharex=True)
output.intensity.plot(ax=axarr[0], marker = "o")
axarr[0].set_ylabel("Intensity")
output.volume.plot(ax=axarr[1], marker = "o")
axarr[1].set_ylabel("Volume")
plt.savefig(outputdir + "/global/global_bouldering_evolution.pdf")
plt.close()

for climber in output.volume.keys():
  cpath = outputdir + "/" + climber.replace(" ", "_")
  if os.path.isdir(cpath) == False: os.mkdir(cpath)

  fig, axarr = plt.subplots(2, figsize=(7,7), sharex=True)
  output.intensity[climber].plot(ax=axarr[0], marker = "o")
  axarr[0].set_ylabel("Intensity")
  output.volume[climber].plot(ax=axarr[1], marker = "o")
  axarr[1].set_ylabel("Volume")
  plt.savefig(cpath + "/{0}_bouldering_evolution.pdf".format(climber))
  plt.close()

# ROUTE
fig = plt.figure()
output2.intensity.plot(marker = "o")
plt.ylabel("Intensity")
plt.savefig(outputdir + "/global/global_route_evolution.pdf")
plt.close()           

for climber in output2.intensity.keys():
  cpath = outputdir + "/" + climber.replace(" ", "_")
  if os.path.isdir(cpath) == False: os.mkdir(cpath)
  
  fig = plt.figure()
  output2.intensity[climber].plot(marker = "o")
  plt.ylabel("Intensity")
  plt.savefig(cpath + "/{0}_route_evolution.pdf".format(climber))
  plt.close()

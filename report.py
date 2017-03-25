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
                     
#-------------------------------------------------------------------------------
# AND PLOT !
fig = plt.figure()
output.intensity.plot()
plt.ylabel("Intensity")
plt.savefig(outputdir + "/global/global_intensity.pdf")
plt.close()

fig = plt.figure()
output.volume.plot()
plt.ylabel("Volume")
plt.savefig(outputdir + "/global/global_volume.pdf")
plt.close()                     
 
for climber in output.volume.keys():
  cpath = outputdir + "/" + climber.replace(" ", "_")
  if os.path.isdir(cpath) == False: os.mkdir(cpath)

  fig = plt.figure()
  output.intensity[climber].plot()
  plt.ylabel("Intensity")
  plt.savefig(cpath + "/{0}_intensity.pdf".format(climber))
  plt.close()
           
  fig = plt.figure()
  output.volume[climber].plot()
  plt.ylabel("Volume")
  plt.savefig(cpath + "/{0}_volume.pdf".format(climber))
  plt.close()
                     
 

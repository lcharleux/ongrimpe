# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Analyseur d'entrainment de grimpe
#------------------------------------------------------------------------------- 


#------------------------------------------------------------------------------- 
# PACKAGES
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#------------------------------------------------------------------------------- 


#------------------------------------------------------------------------------- 
# USEFUL FUNCTIONS
# from: http://stackoverflow.com/questions/6170246/how-do-i-use-matplotlib-autopct
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{v:d} ({p:.2f}%)'.format(p=pct,v=val)
    return my_autopct
#------------------------------------------------------------------------------- 

#------------------------------------------------------------------------------- 
# GETTING DATA FROM GOOGLE DOCS AND PREPROCESSING
path = "https://docs.google.com/spreadsheets/d/1fu1ozajGPJdQnta2Ex3NUbRIV6DadZis0iLIc0Yh0b4/pub?output=csv"
data = pd.read_csv(path, 
                   #parse_dates=['Date']
                  )
# Removing "\n" googlesheet puts randomly
data.columns = [k.replace("\n", "") for k in data.keys()] 
def removeLineBreaks(v):
  if type(v) == str:
    return v.replace("\n", "")
  else:
    return v  
data = data.applymap(removeLineBreaks)

# Processing dates
def processDates(v):
  return "{1}/{0}/{2}".format(*v.split("/"))
data.Date = pd.to_datetime(data.Date.map(processDates))  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# PROCESSING DATA
''' # Work in progress
def plot_difficulty_repartition(session, climber):
  s = pd.DatetimeIndex((session, ))[0]
  d = data[(data.Date == session) & (data.Grimpeur == climber)]
  d = d.groupby(["Niveau", "Etat"]).size()
  #d = d.groupby("Niveau").size()
  fig = plt.figure()
  ax = fig.add_subplot(1,1,1)
  d.plot(kind= "bar")
  plt.savefig("{0}_{1}_routes_by_level.pdf".format(
    "{0}-{1}-{2}".format(s.year, s.month, s.day),
    climber))
  """
  ax.set_aspect("equal")
  plt.pie(d, labels = d.keys(),
     autopct=make_autopct(d.as_matrix()), 
     shadow=True, startangle=90,
     radius=0.45, center=(.5, .5), frame=False)
  
  levels = d.index
  
  ax.bar()
  plt.xlim(0., 1.)
  plt.ylim(0., 1.)
  plt.savefig("{0}_{1}_routes_by_level.pdf".format(
    "{0}-{1}-{2}".format(s.year, s.month, s.day),
    climber))
  """

climbers = data.Grimpeur.unique() # List of registered climbers
walls = data.Salle.unique()       # List of registers walls
sessions = data.Date.unique()

for session in sessions:
  for climber in climbers:
    plot_difficulty_repartition(session, climber)
'''



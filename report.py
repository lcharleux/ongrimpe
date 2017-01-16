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
def plot_difficulty_repartition(session, climber):
  s = pd.DatetimeIndex((session, ))[0]
  d = data[(data.Date == session) & (data.Grimpeur == climber)]
  df2 = pd.DataFrame(index = d.Niveau.unique()).sort_index()
  for e in d.Etat.unique(): df2[e] = d[d.Etat == e].groupby("Niveau").size()
  df3 = pd.DataFrame(index = df2.index, columns = state)
  for k in state_abbr:
    if k in df2.keys():
      df3[state_dict[k]] = df2[k]
  df3.fillna(0) 
  #df2.sort_index(inplace = True)  
  fig = plt.figure()
  df3.plot(kind = "bar")
  plt.grid()
  plt.xlabel("Niveau")
  plt.ylabel(u"Quantité")
  plt.title("{0} {1}".format(
    "{0}/{1}/{2}".format(s.day, s.month, s.year),
    climber))
  plt.savefig("{0}_{1}_routes_by_level.pdf".format(
    "{0}-{1}-{2}".format(s.year, s.month, s.day),
    climber))
  
def plot_state_repartition(session, climber):
  s = pd.DatetimeIndex((session, ))[0]
  d = data[(data.Date == session) & (data.Grimpeur == climber)]
  df2 = pd.DataFrame(index = d.Niveau.unique()).sort_index()
  for e in state_abbr: df2[e] = d[d.Etat == e].groupby("Niveau").size()
  df3 = pd.DataFrame(index = df2.index, columns = state)
  for k in state_abbr:
    if k in df2.keys():
      df3[state_dict[k]] = df2[k]
  etats = []
  for i in range(5): etats.append(df3.fillna(0).sum()[i])
  fig = plt.figure(figsize=(6,6))
  explode=(0, 0, 0, 0, 0.15)
  plt.pie(etats, explode=explode, labels=state, autopct='%1.1f%%', startangle=90, shadow=True)
  plt.axis('equal')
  plt.title("{0} {1}".format(
    "{0}/{1}/{2}".format(s.day, s.month, s.year),
    climber))
  plt.savefig("{0}_{1}_states_repartition.pdf".format(
    "{0}-{1}-{2}".format(s.year, s.month, s.day),
    climber))

def plot_level_evolution(climber):
    s = pd.DatetimeIndex((session, ))[0]
    d = data[data.Grimpeur == climber]
    df2 = pd.DataFrame(index = d.Niveau.unique()).sort_index()
    for e in state_abbr: df2[e] = d[d.Etat == e].groupby("Niveau").size()
    df2 = df2.fillna(0)
    m = []
    for e in state_abbr:
        mi = 0
        si = 0
        for i in range(df2.index.size):
            mi += df2.index[i] * df2[e].values[i]
            si += df2[e].values[i]
        if si == 0:
            m.append(mi)
        else:
            mi = mi / si
            m.append(mi)
    niv_seance = 0.75 * (m[0] + m[1] + m[2]) / 3 + 0.25 * m[3]
    fig = plt.figure()
    plt.plot(session, niv_seance, 'ro')
    plt.grid()
    plt.xlabel("Sessions")
    plt.ylabel("Niveau moyen")
    plt.title("Niveau moyen {0}".format(climber))
    plt.savefig("{0}_level_evolution.pdf".format(climber))
    
    
climbers = data.Grimpeur.unique() # List of registered climbers
walls = data.Salle.unique()       # List of registers walls
sessions = data.Date.unique()
state_abbr = ["O", "F", "S", "R", "E"]
state = ["Onsight","Flash","Pinkpoint","Repeat","Fail"]
state_dict = {k:v for k, v in zip(state_abbr,state)}

           
for session in sessions:
  for climber in climbers:
    plot_difficulty_repartition(session, climber)
    plot_state_repartition(session, climber)
    plot_level_evolution(climber)



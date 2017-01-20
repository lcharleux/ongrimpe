# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Analyseur d'entrainement de grimpe
#------------------------------------------------------------------------------- 


#------------------------------------------------------------------------------- 
# PACKAGES
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
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
# PLOT FUNCTIONS
def plot_difficulty_repartition(session, climber):
  """
  Bar plot of the difficulty repartition of a given climber on a given session.
  """
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
  #plt.grid()
  plt.xlabel("Niveau")
  plt.ylabel("Quantité")
  plt.title("{0} {1} {2}".format(
    "{0}/{1}/{2}".format(s.day, s.month, s.year),
    climber, d.Salle.unique()[0]))
  plt.savefig("{0}_{1}_routes.pdf".format(
    "{0}-{1}-{2}".format(s.year, s.month, s.day),
    climber))
    
def plot_state_repartition(session, climber):
  """
  Pie plot of the state repartition of a given climber on a given session.
  """
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
  fig = plt.figure(figsize=(6,7))
  explode=(0, 0, 0, 0, 0.15)
  plt.pie(etats, explode=explode, labels=state, autopct='%1.1f%%', startangle=90, shadow=True)
  plt.axis('equal')
  plt.title("{0} {1} {2}".format(
    "{0}/{1}/{2}".format(s.day, s.month, s.year),
    climber, d.Salle.unique()[0]))
  plt.savefig("{0}_{1}_repartition.pdf".format(
    "{0}-{1}-{2}".format(s.year, s.month, s.day),
    climber))

def level_session_bouldering(session, climber):
  """
  Compute of the average level of a climber on sessions of bouldering in Cortigrimpe.
  """
  ## à essayer pour retrouver les 3 meilleurs blocs en O, F ou S :
  ## data.groupby(["Grimpeur", "Niveau", "Etat"]).size()

  s = pd.DatetimeIndex((session, ))[0]
  d = data[(data.Date == session) & (data.Grimpeur == climber)]
  df2 = pd.DataFrame(index = d.Niveau.unique()).sort_index()
  for e in state_abbr: df2[e] = d[d.Etat == e].groupby("Niveau").size()
  df2 = df2.fillna(0)
  OFS = []

  for etat, group in d.groupby("Etat"):
      print(etat,
            group.Niveau.sort_values()[group.Niveau.sort_values().index[-1]],
            #group.Niveau.sort_values()[group.Niveau.sort_values().index[-2]],
            #group.Niveau.sort_values()[group.Niveau.sort_values().index[-3]]
            )

#  m1 = 0
#  s1 = 0
#  for e in ['O', 'F', 'S']:
#      for i in range(df2.index.size):
#          m1 += df2.index[i] * df2[e].values[i]
#          s1 += df2[e].values[i]
#  if s1 != 0:
#      m1 = m1 / s1
#  else:
#      m1 = 0
#  m2 = 0
#  s2 = 0
#  for i in range(df2.index.size):
#      m2 += df2.index[i] * df2['R'].values[i]
#      s2 += df2['R'].values[i]
#  if s2 != 0:
#      m2 = m2 / s2
#  else:
#      m2 = 0
#  niv_seance = 0.75 * m1 + 0.25 * m2
#  return niv_seance
  
def plot_level_evolution_bouldering(climber):
  """
  Plot of the average level in bouldering in Cortigrimpe.
  """
  niveau = []
  for session in sessions:
      if data[data.Date == session].Salle.unique() == 'Cortigrimpe':
          niveau.append(level_session_bouldering(session, climber))
  fig = plt.figure()
  plt.plot(sessions, niveau, 'ro-')
  plt.grid()
  plt.xlabel("Sessions")
  plt.ylabel("Niveau moyen")
  plt.title("Niveau moyen {0} à Cortigrimpe".format(climber))
  plt.savefig("{0}_evolution.pdf".format(climber))
        
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# PROCESSING DATA
climbers = data.Grimpeur.unique() # List of registered climbers
walls = data.Salle.unique()       # List of registers walls
sessions = data.Date.unique()
state_abbr = ["O", "F", "S", "R", "E"]
state = ["Onsight","Flash","Sorti","Répèt","Echec"]
state_dict = {k:v for k, v in zip(state_abbr,state)}
           
for session in sessions:
  for climber in data[data.Date == session].Grimpeur.unique():
    plot_difficulty_repartition(session, climber)
    plot_state_repartition(session, climber)
    level_session_bouldering(session, climber)

#for climber in climbers:
#    plot_level_evolution_bouldering(climber)
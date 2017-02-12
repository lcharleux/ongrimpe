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
def plot_difficulty_state_repartition(session, climber):
  """
  Bar plot of the difficulty repartition and pie plot of the state repartition,
  for a given climber on a given session.
  """
  s = pd.DatetimeIndex((session, ))[0]
  d = data[(data.Date == session) & (data.Grimpeur == climber)]
  df2 = pd.DataFrame(index = d.Niveau.unique()).sort_index()
  for e in d.Etat.unique(): df2[e] = d[d.Etat == e].groupby("Niveau").size()
  df3 = pd.DataFrame(index = df2.index, columns = state)
  for k in state_abbr:
    if k in df2.keys():
      df3[state_dict[k]] = df2[k]
  df3 = df3.fillna(0)
  
  df4 = pd.DataFrame(index = d.Niveau.unique()).sort_index()
  for e in state_abbr: df4[e] = d[d.Etat == e].groupby("Niveau").size()
  df5 = pd.DataFrame(index = df4.index, columns = state)
  for k in state_abbr:
    if k in df4.keys():
      df5[state_dict[k]] = df4[k]
  etats = []
  for i in range(5): etats.append(df5.fillna(0).sum()[i])
  explode=(0, 0, 0, 0, 0.15)
  
  fig = plt.figure(figsize = (12, 6))
  ax1 = plt.subplot2grid((1,3), (0,0), colspan = 2)
  ax1.set_xlabel("Niveau")
  ax1.set_ylabel(u"Quantité")
  df3.plot(kind = "bar", ax = ax1)
  ax2 = plt.subplot2grid((1,3), (0,2))
  ax2.pie(etats, explode=explode, labels=state, autopct='%1.1f%%', startangle=90, shadow=True)
  ax2.axis('equal')
  plt.suptitle("{0} {1} {2}".format(
    "{0}/{1}/{2}".format(s.day, s.month, s.year),
    climber, d.Salle.unique()[0]))
  fig.savefig("{0}_{1}.pdf".format(
    "{0}-{1}-{2}".format(s.year, s.month, s.day),
    climber))

def plot_level_evolution_bouldering(climber):
  """
  Plot of the average level in bouldering (in Cortigrimpe).
  """
  maxs = []
  sessions_corti = []
  volume = []
  for session in data[data.Grimpeur == climber].Date.unique():
      if data[data.Date == session].Salle.unique() == 'Cortigrimpe':
          s = pd.DatetimeIndex((session, ))[0]
          d = data[(data.Date == session) & (data.Grimpeur == climber)]
          df2 = pd.DataFrame(index = d.Niveau.unique()).sort_index()
          for e in state_abbr: df2[e] = d[d.Etat == e].groupby("Niveau").size()
          df2 = df2.fillna(0)
          etats = []
          maxs_session = []
          for etat in state_abbr:
              s = 0
              for i in range(len(df2[etat])):
                  s += df2[etat][i]
              if s == 0:
                  etats.append(etat)
                  maxs_session.append(0)
          for etat,group in d.groupby("Etat"):
              if etat in ['O', 'F', 'R', 'S']:
                  etats.append(etat)
                  maxs_session.append(float(max(group.Niveau.sort_values())))
          maxs_dict = {k:v for k, v in zip(etats,maxs_session)}
          maxs.append(maxs_dict)
          sessions_corti.append(session)
          
          vol = 0
          for etat in ['O', 'F', 'R', 'S']:
              for i in range(len(df2[etat])):
                  vol += df2[etat][i]
          volume.append(vol)
          
  df = pd.DataFrame(index = sessions_corti, columns = ["Onsight","Flash","Sorti",u"Répèt"])
  for etat in ['O', 'F', 'R', 'S']:
      for session in range(len(sessions_corti)):
          df[state_dict[etat]][session] = maxs[session][etat]
  df2 = pd.DataFrame(index = sessions_corti, columns = ["Volume"])
  for session in range(len(sessions_corti)):
      df2['Volume'][session] = volume[session]

  fig, axes = plt.subplots(figsize = (14,6), ncols=2, sharey=True)
  df.plot(kind = "barh", ax = axes[0])
  df2.plot(kind = "barh", ax = axes[1])
  axes[0].set(title='Niveau du meilleur bloc')
  axes[1].set(title='Nombre de blocs réussis')
  axes[0].invert_xaxis()
  axes[0].invert_yaxis()
  axes[0].yaxis.tick_right()
  plt.suptitle(u"Evolution de {0} à Cortigrimpe".format(climber))
  plt.savefig("Evolution_{0}_bouldering.pdf".format(climber))
  
def plot_level_evolution_sportclimbing(climber):
  """
  Plot of the average level in sportclimbing (in Glaisins).
  """
  maxs = []
  sessions_voies = []
  volume = []
  for session in data[data.Grimpeur == climber].Date.unique():
      if data[data.Date == session].Salle.unique() == 'Glaisins':
          s = pd.DatetimeIndex((session, ))[0]
          d = data[(data.Date == session) & (data.Grimpeur == climber)]
          df2 = pd.DataFrame(index = d.Niveau.unique()).sort_index()
          for e in state_abbr: df2[e] = d[d.Etat == e].groupby("Niveau").size()
          df2 = df2.fillna(0)
          etats = []
          maxs_session = []
          for etat in state_abbr:
              s = 0
              for i in range(len(df2[etat])):
                  s += df2[etat][i]
              if s == 0:
                  etats.append(etat)
                  maxs_session.append(0)
          for etat,group in d.groupby("Etat"):
              if etat in ['O', 'F', 'R', 'S']:
                  etats.append(etat)
                  if len(max(group.Niveau.sort_values())) == 1:
                      maxs_session.append(float(max(group.Niveau.sort_values())[0]))
                  elif len(max(group.Niveau.sort_values())) > 1:
                      m = float(max(group.Niveau.sort_values())[0])
                      if max(group.Niveau.sort_values())[1] == 'a':
                          m += 0
                          if len(max(group.Niveau.sort_values())) == 3:
                              m += 0.15
                      elif max(group.Niveau.sort_values())[1] == 'b':
                          m += 0.3
                          if len(max(group.Niveau.sort_values())) == 3:
                              m += 0.15
                      elif max(group.Niveau.sort_values())[1] == 'c':
                          m += 0.6
                          if len(max(group.Niveau.sort_values())) == 3:
                              m += 0.15
                  maxs_session.append(float(m))
          maxs_dict = {k:v for k, v in zip(etats,maxs_session)}
          maxs.append(maxs_dict)
          sessions_voies.append(session)
          
          vol = 0
          for etat in ['O', 'F', 'R', 'S']:
              for i in range(len(df2[etat])):
                  vol += df2[etat][i]
          volume.append(vol)
          
  df = pd.DataFrame(index = sessions_voies, columns = ["Onsight","Flash","Sorti",u"Répèt"])
  for etat in ['O', 'F', 'R', 'S']:
      for session in range(len(sessions_voies)):
          df[state_dict[etat]][session] = maxs[session][etat]
  df2 = pd.DataFrame(index = sessions_voies, columns = ["Volume"])
  for session in range(len(sessions_voies)):
      df2['Volume'][session] = volume[session]

  fig, axes = plt.subplots(figsize = (14,6), ncols=2, sharey=True)
  df.plot(kind = "barh", ax = axes[0])
  df2.plot(kind = "barh", ax = axes[1])
  axes[0].set(title='Niveau de la meilleure voie')
  axes[1].set(title='Nombre de voies réussies')
  axes[0].invert_xaxis()
  axes[0].invert_yaxis()
  axes[0].yaxis.tick_right()
  plt.suptitle(u"Evolution de {0} aux Glaisins".format(climber))
  plt.savefig("Evolution_{0}_sportclimbing.pdf".format(climber))
  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# PROCESSING DATA
climbers = data.Grimpeur.unique() # List of registered climbers
walls = data.Salle.unique()       # List of registers walls
sessions = data.Date.unique()
state_abbr = ["O", "F", "S", "R", "E"]
state = ["Onsight","Flash","Sorti",u"Répèt","Echec"]
state_dict = {k:v for k, v in zip(state_abbr,state)}
           
for session in sessions:
  for climber in data[data.Date == session].Grimpeur.unique():
    plot_difficulty_state_repartition(session, climber)

for climber in climbers:
    plot_level_evolution_bouldering(climber)
    plot_level_evolution_sportclimbing(climber)
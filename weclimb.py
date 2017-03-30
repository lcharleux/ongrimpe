import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import string


################################################################################
# GLOBAL VARIABLES
state_abbr = ["O", "F", "S", "R", "E"]
state = ["Onsight","Flash","Sorti",u"Répèt","Echec"]
state_dict = {k:v for k, v in zip(state_abbr,state)}
################################################################################

################################################################################
# UTILITIES
def removeLineBreaks(v):
  if type(v) == str:
    return v.replace("\n", "")
  else:
    return v 
    
def processDates(v):
  return "{1}/{0}/{2}".format(*v.split("/"))     
################################################################################

################################################################################
def preprocess(googlepath, site_map):
  raw_data = pd.read_csv(googlepath)
  raw_data.columns = [k.replace("\n", "") for k in raw_data.keys()] 
  raw_data = raw_data.applymap(removeLineBreaks)
  raw_data["Multiplicateur"] = raw_data.Multiplicateur.fillna(1)
  raw_data.Date = pd.to_datetime(raw_data.Date.map(processDates))
  cmap = {"date": "Date", 
          "climber":"Grimpeur", 
          "site": "Salle",
          "sector": "Secteur",
          "factor": "Multiplicateur",
          "route_id": "Identifiant",
          "grade": "Niveau",
          "belaying": "Assurage",
          "state": "Etat",
          }
  data = pd.DataFrame({k:raw_data[cmap[k]] for k in cmap.keys() }, 
                       index = raw_data.index)  
  # Belaying conversion
  bmap = {"Tête": "first", "Moulinette":"second"}
  def fbmap(value):
    if value in bmap.keys():
      return bmap[value]
    else:
      return np.nan  
  data["belaying"] = data.belaying.map(fbmap)
  # State conversion
  smap = {"O": "onsight", 
          "R": "repeated",
          "E": "failed",
          "S": "redpoint",
          "F" : "flash",}
  def fsmap(value):
    if value in smap.keys():
      return smap[value]
    else:
      return np.nan  
  data["state"] = data.state.map(fsmap)
  # Site kind
  data["kind"] = data["site"].map(lambda s: site_map[s])
  # Numerical grade
  def grade_map(v):
    out = float(v[0]) 
    if len(v) >1:
      out += string.ascii_lowercase.index(v[1]) / 3
    if len(v) > 2 and v[2] == "+":
      out += 1./6.
    return out  
  data["grade_value"] = data.grade.map(grade_map) 
  # Final sorting
  data = data.sort_values(["date", "climber"])
  # Dates !
  dates = []
  for i in data.date:
    date = str(i).split()[0].split("-")
    dates.append("{0}/{1}/{2}".format(*[v[-2:] for v in date]))
  data.date = dates
  
  return data
################################################################################

"""
################################################################################
# DIFFICULTY REPARTITION
def plot_difficulty_state_repartition(data, session, climber):
  "
  Bar plot of the difficulty repartition and pie plot of the state repartition,
  for a given climber on a given session.
  "
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
################################################################################


################################################################################
# BOULDERING LEVEL EVOLUTION
def plot_level_evolution_bouldering(data, path):
  "
  Plot of the average level in bouldering (in Cortigrimpe).
  "
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
  plt.savefig("{0}/Evolution_{0}_bouldering.pdf".format(cpath))
################################################################################


################################################################################
# SPORTCLIMBING LEVEL EVOLUTION  
def plot_level_evolution_sportclimbing(data, climber):
  "
  Plot of the average level in sportclimbing (in Glaisins).
  "
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
################################################################################
"""

################################################################################
def boulder_volume(data, common_ratio = 1.5, ref_grade = 1):
    """
    Computes the volume of each climber during each session. Boulder difficulty
    is scaled using
    """
    
    data = data.loc[data.kind == "boulder"]
    data = pd.concat([data.loc[data.state == "onsight"], 
                      data.loc[data.state == "flash"],
                      data.loc[data.state == "redpoint"],
                      data.loc[data.state == "repeated"],])
    
    out = data.groupby(["date", "climber", "grade"]).agg(
          {"factor": np.sum})
    out = out.unstack().fillna(0)
    n = out.values
    n *= (common_ratio**(np.array(out.columns.levels[1])
          .astype(np.float64)- ref_grade + 1).reshape(n.shape[1]))
    out = pd.DataFrame(n, index = out.index, 
                       columns = out.columns.levels[1]).sum(axis = 1)
    out =  out.unstack()
    out.columns = pd.MultiIndex.from_product([("volume",), 
                                               np.array(out.columns)], 
                                               names = ["output", "climber"])
    return out                                           
################################################################################

################################################################################
def boulder_intensity(data):
    out = []
    data = data.loc[data.kind == "boulder"]
    data = pd.concat([data.loc[data.state == "onsight"], 
                      data.loc[data.state == "flash"],
                      data.loc[data.state == "redpoint"],])
    for climber, group in data.groupby("climber"):
      difficulty = []
      dates = []
      for date, group2 in group.groupby("date"):
        mg = group2.grade_value.max()
        fac = group2.loc[group2.grade_value == mg].factor.sum()
        diff = mg + ((2**np.arange(1, fac, dtype = np.float64))**(-1)).sum()
        dates.append(date)
        difficulty.append(diff)
      df = pd.DataFrame(difficulty, index = dates)
      df.columns = pd.MultiIndex.from_tuples([("intensity", climber)], 
                                               names = ["output", "climber"])
      df.index.name = "session"
      out.append(df)
    out = pd.concat(out, axis = 1)
    return out
################################################################################

################################################################################
#def route_volume(data, common_ratio = 1.5, ref_grade = 1):   
#    data = data.loc[data.kind == "route"]
#    data = pd.concat([data.loc[data.state == "onsight"], 
#                      data.loc[data.state == "flash"],
#                      data.loc[data.state == "redpoint"],
#                      data.loc[data.state == "repeated"],])
#    
#    out = data.groupby(["date", "climber", "grade"]).agg(
#          {"factor": np.sum})
#    out = out.unstack().fillna(0)
#    n = out.values
#    n *= (common_ratio**(np.array(out.columns.levels[1])
#          .astype(np.float64)- ref_grade + 1).reshape(n.shape[1]))
#    out = pd.DataFrame(n, index = out.index, 
#                       columns = out.columns.levels[1]).sum(axis = 1)
#    out =  out.unstack()
#    out.columns = pd.MultiIndex.from_product([("volume",), 
#                                               np.array(out.columns)], 
#                                               names = ["output", "climber"])
#    return out   
################################################################################

################################################################################
def route_intensity(data):
    out = []
    data = data.loc[data.kind == "route"]
    data = pd.concat([data.loc[data.state == "onsight"], 
                      data.loc[data.state == "flash"],
                      data.loc[data.state == "redpoint"],])
    for climber, group in data.groupby("climber"):
      difficulty = []
      dates = []
      for date, group2 in group.groupby("date"):
        mg = group2.grade_value.max()
        fac = group2.loc[group2.grade_value == mg].factor.sum()
        diff = mg + ((2**np.arange(1, fac, dtype = np.float64))**(-1)).sum()
        dates.append(date)
        difficulty.append(diff)
      df = pd.DataFrame(difficulty, index = dates)
      df.columns = pd.MultiIndex.from_tuples([("intensity", climber)], 
                                               names = ["output", "climber"])
      df.index.name = "session"
      out.append(df)
    out = pd.concat(out, axis = 1)
    return out
################################################################################

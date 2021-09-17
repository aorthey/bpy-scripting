import numpy as np
import sys, os 
import re
from xml.dom.minidom import parse

class PathKeyframe():
  time = 0
  states = []
  name = ""
  def __init__(self, name, time, states):
    self.time = time
    self.states = states
    self.name = "keyframe"+name+str(int(self.time))

class Path():

  # name = ""
  # timeStart = 1000
  # timeEnd = 0
  # Nstates = 0

  def __init__(self, filename):
    self.Nstates = 0
    self.keyframes = []
    self.timeEnd = 0
    self.timeStart = 1000
    self.name = ""
    self.to_be_removed = False

    doc = parse(filename)
    self.name = os.path.basename(filename)

    removals = doc.getElementsByTagName("removal")
    for removal in removals:
      self.removal_time = float(removal.getAttribute('time'))
      self.to_be_removed = True

    keyframes = doc.getElementsByTagName("keyframe")
    for keyframe in keyframes:
        states = keyframe.getElementsByTagName("state")
        N = len(states)
        if N > self.Nstates:
          self.Nstates = N

    for keyframe in keyframes:
        time = int(float(keyframe.getAttribute('time')))
        if time > self.timeEnd:
          self.timeEnd = time
        if time < self.timeStart:
          self.timeStart = time

        states = keyframe.getElementsByTagName("state")

        P = np.empty((0,3), float)

        for (k,state) in enumerate(states):
          config = state.firstChild.nodeValue
          config = config.split(" ")
          if len(config) > 5:
            p = np.array([[config[2],config[3],config[4]]])
          else:
            p = np.array([[config[2],config[3],0]])
          # P[k,0] = config[2]
          # P[k,1] = config[3]
          P = np.append(P, p, axis=0)

        while len(P) < self.Nstates:
          P = np.append(P, p, axis=0)

        P = P.astype(float)

        self.keyframes.append(PathKeyframe(self.name, time, P))

    print("Path ",self.name," has ",len(self.keyframes),"keyframes.")


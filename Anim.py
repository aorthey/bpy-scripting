import numpy as np
import sys, os 
import re


colorDataBase = {
"purplePosy " :  (236/256.0, 223/256.0, 237/256.0, 1.0)
,"rococoRose " :  (221/256.0, 146/256.0, 155/256.0, 1.0)
,"seasideSpray " :  (183/256.0, 204/256.0, 226/256.0, 1.0)
,"blushingBride " :  (249/256.0, 194/256.0, 188/256.0, 1.0) #cherry red
,"calypsoCoral " :  (241/256.0, 116/256.0, 91/256.0, 1.0) #calypso red
,"petalPink " :  (252/256.0, 206/256.0, 182/256.0, 1.0) #pink-ish
,"soSaflron " :  (255/256.0, 218/256.0, 141/256.0, 1.0) #yellow-ish
,"softSeaFoam " :  (234/256.0, 241/256.0, 213/256.0, 1.0) #soft green-ish
,"pearPizzazz " :  (184/256.0, 192/256.0, 104/256.0, 1.0) #dark green-ish
,"mintMacaron " :  (159/256.0, 197/256.0, 170/256.0, 1.0) #mint-ish
,"poolParty " :  (171/256.0, 217/256.0, 213/256.0, 1.0) #aqua green-ish
,"balmyBlue " :  (169/256.0, 214/256.0, 235/256.0, 1.0) #blue-ish
,"highlandHeather " :  (173/256.0, 153/256.0, 200/256.0, 1.0)  #magenta-ish
}

def projectColor(color):
  bestDistance = float('inf')
  nearestColor = color
  for cname in colorDataBase:
    cdb = colorDataBase[cname]
    d = np.linalg.norm(color - cdb)
    if d < bestDistance:
      bestDistance = d
      nearestColor = cdb

  return nearestColor

class Segment():

  timeStart = 0
  timeEnd = 0
  names = []
  q = []
  c = []

  def __init__(self, timeStart, names, q):
    self.timeStart = int(timeStart)
    self.names = names
    self.q = q
    self.timeEnd = q.shape[0] + self.timeStart

  def setColor(self, c):
    self.c = c

  def getPoses(self, time, name):
    if time < self.timeStart:
      time = self.timeStart
    if time > self.timeEnd:
      time = self.timeEnd

    ctr = 0
    for k in range(0,len(self.names)):
      if name == self.names[k]:
        ctr = k
        break
    return self.q[time-self.timeStart, ctr]

  def getColor(self, name):
    ctr = 0
    for k in range(0,len(self.names)):
      if name == self.names[k]:
        ctr = k
        break
    color = self.c[ctr]
    return color
    # pcolor = projectColor(color)
    # return pcolor


class Anim():

  segments = []
  numSegments = 0

  def __init__(self, fname):
    f = open(fname, 'r')
    line = f.readline()
    if not line:
      print("Animation corrupted")
      return
    else:
      p = re.match(r'.*<([0-9]+)>', line)
      self.numSegments = p.group(1)

    ctrSegments = 0
    while True:
      line = f.readline()
      if not line:
        break
      p = re.match(r'^start', line)
      ## START DETECTED
      if p is not None:
        p = re.match(r'.*<([0-9]+)> ([0-9]+)', line)
        timeStart = p.group(2)
        print("Segment ",ctrSegments," starts at timeframe ",timeStart)

        ## EXTRACT FRAMENAMES
        lineIDs = f.readline()
        if not lineIDs:
          print("Unknown error")
          break
        lineNames = f.readline()
        if not lineNames:
          print("Unknown error")
          break
        
        p = re.match(r'.*<([0-9]+)> (.*)]', lineNames)
        framename = p.group(2)
        names = framename.split(" ")

        ## EXTRACT FRAME COLORS
        line = f.readline()
        if not line:
          print("Unknown error")
          break
        p = re.match(r'^frameColors.*<(.*)>', line)
        dims = np.fromstring(p.group(1), dtype='int', sep=' ')
        numColors = dims[0]
        numColorDims = dims[1]
        c = []
        for i in range(0,numColors):
          ck = np.fromstring(f.readline(), dtype='float', sep=' ')
          c.append(ck)
          #empty line

        ## EXTRACT POSES
        line = f.readline()
        print(line)
        if not line:
          print("Unknown error")
          break
        p = re.match(r'^poses.*<(.*)>', line)
        pose = np.fromstring(p.group(1), dtype='int', sep=' ')
        numPoses = pose[0]
        numFrames = pose[1]
        numCoordinates = pose[2]
        q = []
        for i in range(0,pose[0]):
          qi = []
          for k in range(0,pose[1]):
            qk = np.fromstring(f.readline(), dtype='float', sep=' ')
            qi.append(qk)
          q.append(qi)
          #empty line
          f.readline()
        q = np.array(q)
        s = Segment(timeStart, names, q)
        s.setColor(c)
        self.segments.append(s)
        ctrSegments = ctrSegments + 1


    f.close()

    print(self.numSegments+" animation segments found.")


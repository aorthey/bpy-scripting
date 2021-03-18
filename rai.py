import bpy
import bmesh
import numpy as np
import sys, os 
import re
import time
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

from src.Utils import *
from src.Camera import *
from src.RaiLoader import *
from src.RaiAnim import *
from src.RenderEngine import *

time_start_script = time.process_time()

########################################################
# CUSTOM SETTINGS
########################################################
Nsegments = 2 #display N segments. -1: display all segments
NkeyframeSteps = 10 #use every n-th keyframe, interpolate inbetween

renderAnimation = False
renderImage = True
doZoom=True
tPaddingEnd = 250 #number of frames to append after algorithms converged
tZoomStart = 100
tZoomOutDuration = 25
tRotationStart = tZoomStart + 200
cameraLocation = Vector((-6,-12,+5))
cameraFocusPoint = Vector((0,0,0))

folder = "data/animations/all_robots/"
filename = os.path.basename(os.path.dirname(folder))
########################################################
# Load collada file and preprocess the objects
########################################################

rai = RaiLoader(folder)
rai.generateKeyframesFromAnim(Nsegments, NkeyframeSteps)

setBackgroundColor((.2,.2,.2))

###############################################################################
## LIGHTNING
###############################################################################
lightLocation = 0.3*(cameraLocation-cameraFocusPoint)+Vector((0,0,+5))
# addLightSourceSun(lightLocation)
addLightSourcePoint(lightLocation)

###############################################################################
## CAMERA
###############################################################################
bpy.context.scene.frame_end += tPaddingEnd
tend = bpy.context.scene.frame_end 
camera = Camera(cameraLocation, cameraFocusPoint)

if doZoom:
    camera.zoomIn(tZoomStart, tZoomStart+50)
    camera.zoomOut(tZoomStart+50+50, tZoomStart+50+50+tZoomOutDuration)
camera.rotate(tRotationStart, tend)

## set view to camera
for area in bpy.context.screen.areas:
  if area.type == 'VIEW_3D':
    area.spaces[0].region_3d.view_perspective = 'CAMERA'
    break

###############################################################################
## RENDERING
###############################################################################

render = RenderEngine(folder)

if renderImage:
  render.LastFrameToPNG(filename = dirname+"/"+filename+'.png')

if renderAnimation:
  render.toMP4(dirname+"/"+filename+".mp4")

elapsed_time = time.process_time() - time_start_script
print("TIME for RENDERING: %f (in s), %f (in m), %f (in h)"%\
    (elapsed_time,elapsed_time/60,elapsed_time/60/60))

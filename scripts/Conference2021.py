import bpy
import bmesh
import numpy as np
import sys, os 
import re
import time
dirname = os.path.dirname(os.path.realpath(__file__+"/.."))
sys.path.append(dirname)

from src.Utils import *
from src.RaiAnim import *
from src.Camera import *

time_start_script = time.process_time()

########################################################
# CUSTOM SETTINGS
########################################################
Nsegments = 2 #display N segments. -1: display all segments
NkeyframeSteps = 10 #use every n-th keyframe, interpolate inbetween

# renderAnimation = True
renderAnimation = False
doZoom=True
tPaddingEnd = 250 #number of frames to append after algorithms converged
tZoomStart = 100 ##frame at which we start to rotate camera
tZoomOutDuration = 25
tRotationStart = tZoomStart + 200
cameraLocation = Vector((-6,-12,+5))
cameraFocusPoint = Vector((0,0,0))

folder = "data/animations/20210215_141740/"
folder = "data/animations/20210216_001730/"
folder = "data/animations/20210216_204609/" ## tower, 4agents, 1crane
folder = "data/animations/20210218_214753/" ##pyramid

folder = "data/animations/Julius_well/" ## well (Julius, 2 agents)

folder = "data/animations/20210223_192210/" ##FIT building, 6 agents
folder = "data/animations/20210223_112459/" ## well (valentin, 6 agents)
folder = "data/animations/20210218_173654/" ## wall
folder = "data/animations/20210221_004210/" ## tower
folder = "data/animations/20210226_124540/" ## tower (4kuka, 4mobile)
folder = "data/animations/20210226_130645/" ## tower (4kuka, 4mobile, 1crane)

folder = "data/animations/fit/" ##final FIT (6+6 agents)
folder = "data/animations/wall/" ##final wall (6+6 agents)
folder = "data/animations/20210226_135839/" ## tower (right colors)
folder = "data/animations/handover/" ##Final Tower Handover
folder = "data/animations/all_robots/" ##Group Picture

filename = os.path.basename(os.path.dirname(folder))

if "fit" in filename:
  tZoomOutDuration = 35
if "20210226_135839" in filename:
  tZoomOutDuration = 40
if "handover" in filename:
  doZoom=False
  cameraLocation = Vector((-14,-20,+9))
  tRotationStart = 0
  tZoomOutDuration = 40

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
########################################################
# Load collada file and preprocess the objects
########################################################

fname = os.path.abspath(dirname+"/" + folder + "initial.dae")
A = Anim(folder + "/Anim.txt")

c = bpy.ops.wm.collada_import(filepath=fname, import_units=True, auto_connect=False)

bpy.ops.object.select_all(action='SELECT')

objs = bpy.context.selected_objects

curves = {}
for obj in objs:
  if "gripper" in obj.name:
    curveDynamic = addBezierCurve(obj.name)
    curves[obj.name] = curveDynamic
  obj.location = [0,-1000,-1000]
  if obj.name == "plate":
    bpy.context.scene.frame_set(0)
    obj.location = [0,0,-0.15]
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = [1,0,0,0]
    obj.parent = None
    obj.keyframe_insert(data_path="location", index=-1)
    obj.keyframe_insert(data_path="rotation_quaternion", index=-1)
    # addMaterialConcrete(obj)
    addMaterialColor(obj, (0.6,0.6,0.6,1.0))

########################################################
# Load collada file and preprocess the objects
########################################################

setBackgroundColor((.2,.2,.2))

bpy.ops.object.select_all(action='SELECT')

ctr = 0
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 0
for segment in A.segments:
  if ctr > Nsegments and Nsegments >= 0:
    break
  ctr = ctr + 1
  for n in range(0,len(segment.names)):
    name = segment.names[n]

    if segment.timeEnd > bpy.context.scene.frame_end:
      bpy.context.scene.frame_end = segment.timeEnd

    print("Import segment %d/%d [time %d,%d] (link %s %d/%d)"\
        %(ctr,(Nsegments+1 if Nsegments>=0 else len(A.segments)),
          segment.timeStart,segment.timeEnd, name, n,len(segment.names)))

    for obj in bpy.context.selected_objects:
      if obj.name != name:
        continue
      if "coll" in name:
        continue
      # if '_' in obj.name:
      #   continue

      ## FIXED CURVE FOR DEBUGGING
      # if obj.name == name and "gripper" in obj.name:
      #   T = range(segment.timeStart, segment.timeEnd)
      #   Ng = len(T)-1
      #   curveObject = addBezierCurve(obj.name+"trail", Ng, 0.005)
      #   P = curveObject.data.splines[0].points
      #   for t in T:
      #     pose = segment.getPoses(t, obj.name)
      #     p = P[t-segment.timeStart]
      #     p.co = (pose[0], pose[1], pose[2], 1.0)

      for t in range(segment.timeStart, segment.timeEnd, NkeyframeSteps):
        pose = segment.getPoses(t, name)
        color = segment.getColor(name)
        bpy.context.scene.frame_set(t)
        obj.location = pose[0:3]
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = pose[3:]
        obj.parent = None
        obj.keyframe_insert(data_path="location", index=-1)
        obj.keyframe_insert(data_path="rotation_quaternion", index=-1)
        for fcurve in obj.animation_data.action.fcurves:
          kf = fcurve.keyframe_points[-1]
          kf.interpolation = 'CONSTANT'

        # pattern = re.compile(r'^(b|node)[0-9]+')
        # if pattern.match(obj.name):
        if '_' not in obj.name:
          # print("Add glass material.")
          addMaterialGlass(obj)
        else:
          addMaterialColor(obj, color)

        if "gripper" in obj.name:
          P = curves[obj.name].data.splines[0].points
          addMaterialColor(curves[obj.name], color)
          material = curves[obj.name].active_material
          material.shadow_method = 'NONE'
          curves[obj.name].cycles_visibility.shadow = False
          material.use_nodes = True
          bsdf = material.node_tree.nodes["Principled BSDF"]
          bsdf.inputs['Base Color'].default_value = color

          L = len(P)
          for ctrPts in range(0, L):
            tval = t - ctrPts
            if tval > 0:
              cPose = segment.getPoses(tval, name)
            else:
              cPose = segment.getPoses(0, name)
            p = P[ctrPts]
            #Ordering of points: left is current in time, right is back in time
            p.co = (cPose[0], cPose[1], cPose[2], 1.0)

            ##Attempt at letting path fade out (does not work yet)
            alpha = 1.0 - float(ctrPts)/float(L)
            slot = curves[obj.name].material_slots[0]
            slot.material.diffuse_color[3] = alpha

            p.keyframe_insert(data_path="co", index=-1)

      ####WEIRD behavior during fadeout
      if "gripper" in obj.name:
        ##add fadeout
        tend = segment.timeEnd

        P = curves[obj.name].data.splines[0].points
        L = len(P)

        if tend+L > bpy.context.scene.frame_end:
          bpy.context.scene.frame_end = tend + L

        for t in range(tend, tend + L):
          bpy.context.scene.frame_set(t)

          for ctrPts in range(0, L):
            tval = t - ctrPts
            if tval <= 0:
              cPose = segment.getPoses(0, name)
            elif tval < tend:
              cPose = segment.getPoses(tval, name)
            else:
              cPose = segment.getPoses(tend-1, name)

            p = P[ctrPts]
            p.co = (cPose[0], cPose[1], cPose[2], 1)
            p.keyframe_insert(data_path="co")


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
#0:0,pick 141,place 56,retract 53;252,pick 48,place 307,retract 52;

#TODO: zoom in/out to specific distance
distance = copy.copy(camera.distance)
if doZoom:
    camera.zoomIn(tZoomStart, tZoomStart+50)
    camera.zoomOut(tZoomStart+50+50, tZoomStart+50+50+tZoomOutDuration)
#camera.rotate(253+10, tend)
camera.rotate(tRotationStart, tend)
# camera.zoomOut(210,400)

## set view to camera
for area in bpy.context.screen.areas:
  if area.type == 'VIEW_3D':
    area.spaces[0].region_3d.view_perspective = 'CAMERA'
    break

###############################################################################
## RENDERING
###############################################################################
renderEngine = bpy.context.scene.render
renderEngine.image_settings.file_format = "FFMPEG"
renderEngine.ffmpeg.format = "MPEG4"
renderEngine.ffmpeg.codec = "H264"
renderEngine.ffmpeg.constant_rate_factor = "HIGH" #MEDIUM, LOW
renderEngine.filepath = dirname+"/"+filename+".mp4"

### Render Animation to MP4 video
if renderAnimation:
  print("Starting to render %d frames."% bpy.context.scene.frame_end)
  bpy.ops.render.render(animation=True)

elapsed_time = time.process_time() - time_start_script
print("TIME for RENDERING: %f (in s), %f (in m), %f (in h)"%\
    (elapsed_time,elapsed_time/60,elapsed_time/60/60))


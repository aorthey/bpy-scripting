import bpy
import bmesh
import numpy as np
import sys, os 
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

from bpy_utils import *
from Anim import *

########################################################
# CUSTOM SETTINGS
########################################################
Nsegments = -1 #display N segments. -1: display all segments
NkeyframeSteps = 1 #use every n-th keyframe, interpolate inbetween
renderAnimation = False
fname = os.path.abspath(dirname+"/data/20210211_2042/initial.dae")
A = Anim("data/20210211_2042/Anim.txt")
# fname = os.path.abspath(dirname+"/data/initial.dae")
# A = Anim("data/Anim.txt")
########################################################

cameraLocation = Vector((-3,-6,+3))
cameraFocusPoint = Vector((0,0,0))

## delete all previous objects in scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

c = bpy.ops.wm.collada_import(filepath=fname, import_units=True, auto_connect=False)

## SELECT ALL OBJECTS IN BLENDER
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
    addMaterialConcrete(obj)

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
        %(ctr,len(A.segments),segment.timeStart,segment.timeEnd, name, n,len(segment.names)))

    for obj in bpy.context.selected_objects:

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

      if obj.name == name and "coll" not in name:
        ## FOUND match between collada object and Anim object for current segment
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
          addMaterialColor(obj, color)
          if "gripper" in obj.name:
            P = curves[obj.name].data.splines[0].points
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
      if obj.name == name and "gripper" in obj.name:
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


filename = "animation"

lightLocation = 0.3*(cameraLocation-cameraFocusPoint)+Vector((0,0,+5))
addLightSourceSun(lightLocation)

addCamera(cameraLocation, cameraFocusPoint)

## set view to camera
for area in bpy.context.screen.areas:
  if area.type == 'VIEW_3D':
    area.spaces[0].region_3d.view_perspective = 'CAMERA'
    break

renderEngine = bpy.context.scene.render
renderEngine.image_settings.file_format = "FFMPEG"
renderEngine.ffmpeg.format = "MPEG4"
renderEngine.ffmpeg.codec = "H264"
renderEngine.ffmpeg.constant_rate_factor = "HIGH" #MEDIUM, LOW
renderEngine.filepath = dirname+"/"+filename+".mp4"

### Render Animation to MP4 video
if renderAnimation:
  bpy.ops.render.render(animation=True)

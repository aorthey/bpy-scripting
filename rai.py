import bpy
import bmesh
import numpy as np
import sys, os 
import re
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

from bpy_utils import *
from Anim import *
from Camera import *

########################################################
# TODO
########################################################

#[x] Better distinction of robot colors

#[ ] Smoother interpolation rot/zoom
#[ ] Better visualization of frame paths
#[ ] Visualize scheduler as guitar hero 
#[x] diffuse on shadow to have smoother edges
#[x] Remove shadow from paths!?
#[x] Project Color onto nearest Pastell Color
#[x] Background color

renderAnimation = False

########################################################
# CUSTOM SETTINGS
########################################################
Nsegments = -1 #display N segments. -1: display all segments
NkeyframeSteps = 1 #use every n-th keyframe, interpolate inbetween
# renderAnimation = True
folder = "data/animations/20210215_141740/"
folder = "data/animations/20210216_001730/"
folder = "data/animations/20210216_204609/" ## tower, 4agents, 1crane
folder = "data/animations/20210218_173654/" ## wall
folder = "data/animations/Julius_well/"
folder = "data/animations/20210218_214753/" ##pyramid
cameraLocation = Vector((-6,-12,+5))
cameraFocusPoint = Vector((0,0,0))
########################################################

fname = os.path.abspath(dirname+"/" + folder + "initial.dae")
A = Anim(folder + "/Anim.txt")

# cameraLocation = Vector((-1.5,-3,+1.5))

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
    # addMaterialConcrete(obj)
    addMaterialColor(obj, (0.6,0.6,0.6,1.0))

### SET BACKGROUND COLOR OF SCENE
world = bpy.context.scene.world
if world is None:
  new_world = bpy.data.worlds.new("New World")
  world = new_world

world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value[:3] = (.2, .2, .2)
bg.inputs[1].default_value = 1.0

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


          pattern = re.compile(r'^(b|node)[0-9]+')
          if pattern.match(obj.name):
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

###############################################################################
## LIGHTNING
###############################################################################
lightLocation = 0.3*(cameraLocation-cameraFocusPoint)+Vector((0,0,+5))
# addLightSourceSun(lightLocation)
addLightSourcePoint(lightLocation)

###############################################################################
## CAMERA
###############################################################################
tend = bpy.context.scene.frame_end
camera = Camera(cameraLocation, cameraFocusPoint)
#0:0,pick 141,place 56,retract 53;252,pick 48,place 307,retract 52;

#TODO: zoom in/out to specific distance
distance = copy.copy(camera.distance)
camera.zoomIn(141, 141+56)
camera.zoomOut(141+56+30, 252)
camera.rotate(253+10, tend)
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

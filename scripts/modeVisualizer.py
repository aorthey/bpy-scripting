import bpy
import bmesh
import numpy as np
import sys, os 
import re
import time
dirname = os.path.dirname(os.path.realpath(__file__+"/.."))
sys.path.append(dirname)

from src.Utils import *
from src.Camera import *
from src.Path import Path
from src.PathArray import PathArray
from src.Colors import materialWhiteTransparent
from src.RenderEngine import RenderEngine
from src.CuttingTools import CuttingTools

time_start_script = time.process_time()

cameraLocation = Vector((+6,0,+6)) #torus
cameraFocusPoint = Vector((0,0,0))

sizeStates = 0.15
renderAnimation=False
renderImage=False
folder = "data/modes/passage/"
folder = "data/modes/multigoal/"
folder = "data/modes/lattice/"
folder = "data/modes/rod/"
folder = "data/modes/jaillet/"
folder = "data/modes/kleinbottle/"
folder = "data/modes/torus/"
folder = "data/modes/sphere/"
folder = "data/modes/mobius/"

filename = os.path.basename(os.path.dirname(folder))

for o in bpy.context.scene.objects:
  o.animation_data_clear()
bpy.context.scene.animation_data_clear()

for o in bpy.data.objects:
  o.animation_data_clear()

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for a in bpy.data.actions:
  bpy.data.actions.remove(a)

for o in bpy.context.scene.objects:
  o.select_set(True)
bpy.ops.object.delete()

bpy.ops.object.select_by_type(type='CURVE')
bpy.ops.object.delete()



########################################################
## DEFINE COLORS
########################################################

bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 0

########################################################
### LOAD CURVES AND OBJECTS
########################################################
fname = os.path.abspath(dirname+"/" + folder + "scene.dae")

########################################################
### CUSTOM CHANGES
########################################################
if "lattice" in folder:
  lightLocation = Vector((0,4,0))
  addLightSourcePoint(lightLocation)

  c = bpy.ops.wm.collada_import(filepath=fname, import_units=True, auto_connect=False)
  cameraLocation = Vector((+3.5,+9.4,+2.3))
  bpy.ops.object.select_all(action='SELECT')
  objs = bpy.context.selected_objects

  for obj in objs:
    if "the_lattice" in obj.name:
      bpy.context.scene.frame_set(0)
      obj.rotation_mode = 'QUATERNION'
      obj.rotation_quaternion = [1,0,0,0]
      obj.keyframe_insert(data_path="rotation_quaternion", index=-1)

  for obj in objs:
    if "body" in obj.name:
      bpy.ops.object.select_all(action='DESELECT')
      obj.select_set(True)
      bpy.ops.object.delete() 
      break


if "mobius" in folder:
  cameraLocation = Vector((3.41,-3.02,2.14))
  cameraFocusPoint = Vector((-0.0,0.0,-0.15))

  R = "(1.0 + v*cos(0.5*u))"
  x_eq = R+"*cos(u)"
  y_eq = R+"*sin(u)"
  z_eq = "v*sin(0.5*u)"
  mobius_mesh = bpy.ops.mesh.primitive_xyz_function_surface(\
      x_eq = x_eq, \
      y_eq = y_eq, \
      z_eq = z_eq, 
			range_u_min=-pi, 
			range_u_max=pi,
			range_u_step=256, 
			wrap_u = False,
			range_v_min=-0.5, 
			range_v_max=+0.5,
			range_v_step=64, 
			wrap_v = False)

  bpy.context.object.name = 'mobius'
  mobius_obj = bpy.data.objects['mobius']
  mobius_obj = bpy.context.active_object

  ## NOTE: primitive_xyz_function_surface sets mode to EDIT
  bpy.ops.object.mode_set(mode='OBJECT') 

  #################################################################################
  #### PUNCTURING OF MOBIUS STRIP
  #################################################################################
  mobius_obj.data.materials.append(materialWhiteTransparent)
  mobius_obj.show_transparent = True #  displays trans in viewport

  cutter = CuttingTools()
  cutter.CutSphericalHole(mobius_obj, location = Vector([0,1.3,-0.3]), diameter=0.5)

if "kleinbottle" in folder:
  cameraLocation = Vector((-1.7,4.7,9.3))
  cameraFocusPoint = Vector((-0.0,2.3,0))

  lightLocation = Vector((0,4,11))
  addLightSourcePoint(lightLocation)

  ## NOTE: Please enable addon "Extra Objects: Mesh"
  a = "(3*cos(v) - 30*sin(u) + 90*pow(cos(u),4)*sin(u)-60*pow(cos(u),6)*sin(u)+5*cos(u)*cos(v)*sin(u))"

  b = "(3*cos(v) - 3*pow(cos(u),2)*cos(v) - 48*pow(cos(u),4)*cos(v) \
  + 48*pow(cos(u),6)*cos(v)\
  -60*sin(u) + 5*cos(u)*cos(v)*sin(u)  \
  -5*pow(cos(u),3)*cos(v)*sin(u)-80*pow(cos(u),5)*cos(v)*sin(u) \
  + 80*pow(cos(u),7)*cos(v)*sin(u))"

  x_eq = "-2.0/15.0*cos(u)*"+a;
  y_eq = "-1.0/15.0*sin(u)*"+b
  z_eq = "2.0/15.0 * (3+5*cos(u)*sin(u)) * sin(v)"

  kleinbottle_mesh = bpy.ops.mesh.primitive_xyz_function_surface(\
      x_eq = x_eq, \
      y_eq = y_eq, \
      z_eq = z_eq, 
			range_u_min=0, 
			range_u_max=pi,
			range_u_step=256, 
			wrap_u = False,
			range_v_min=0.0, 
			range_v_max=2*pi,
			range_v_step=128, 
			wrap_v = True)
      # range_u_step=128)

  bpy.context.object.name = 'kleinbottle'
  kleinbottle_obj = bpy.data.objects['kleinbottle']
  kleinbottle_obj = bpy.context.active_object

  ## NOTE: primitive_xyz_function_surface sets mode to EDIT
  bpy.ops.object.mode_set(mode='OBJECT') 

  #################################################################################
  #### PUNCTURING OF KLEINBOTTLE
  #################################################################################
  kleinbottle_obj.data.materials.append(materialWhiteTransparent)
  kleinbottle_obj.show_transparent = True #  displays trans in viewport

  cutter = CuttingTools()
  cutter.CutSphericalHole(kleinbottle_obj, location = Vector([0,1.3,0.8]), diameter=0.5)


if "jaillet" in folder:
  lightLocation = Vector((-8,0,+6))
  addLightSourcePoint(lightLocation)

  c = bpy.ops.wm.collada_import(filepath=fname, import_units=True, auto_connect=False)
  bpy.ops.object.select_all(action='SELECT')
  objs = bpy.context.selected_objects

  cameraLocation = Vector((-12,4.3,9.7))

  for obj in objs:
    if "plate" in obj.name:
      bpy.context.scene.frame_set(0)
      obj.rotation_mode = 'QUATERNION'
      obj.rotation_quaternion = [1,0,0,0]
      obj.keyframe_insert(data_path="rotation_quaternion", index=-1)
      color = (0.5,0.5,0.5,1.0)
      addMaterialColor(obj, color)

  for obj in objs:
    if "body" in obj.name:
      bpy.ops.object.select_all(action='DESELECT')
      obj.select_set(True)
      bpy.ops.object.delete() 
      break

if "rod" in folder:
  lightLocation = Vector((1.8,3,3.8))
  addLightSourcePoint(lightLocation)

  c = bpy.ops.wm.collada_import(filepath=fname, import_units=True, auto_connect=False)
  cameraLocation = Vector((+1.5*2.5,+1.5*6.7,+3.5))
  cameraLocation = Vector((2.1,7.7,6.6))
  cameraFocusPoint = Vector((0,0,1))

  bpy.ops.object.select_all(action='SELECT')
  objs = bpy.context.selected_objects

  for obj in objs:
    if "plate" in obj.name:
      bpy.context.scene.frame_set(0)
      obj.rotation_mode = 'QUATERNION'
      obj.rotation_quaternion = [1,0,0,0]
      obj.keyframe_insert(data_path="rotation_quaternion", index=-1)
      color = (0.5,0.5,0.5,1.0)
      addMaterialColor(obj, color)
    if "cylinder" in obj.name:
      bpy.context.scene.frame_set(0)
      obj.rotation_mode = 'QUATERNION'
      obj.rotation_quaternion = [1,0,0,0]
      obj.location = (0,0,1)
      obj.keyframe_insert(data_path="rotation_quaternion", index=-1)
      obj.keyframe_insert(data_path="location", index=-1)

      addMaterialToObject(obj, materialWhiteTransparent)

  for obj in objs:
    if "body" in obj.name:
      bpy.ops.object.select_all(action='DESELECT')
      obj.select_set(True)
      bpy.ops.object.delete() 
      break

if "passage" in folder:
  c = bpy.ops.wm.collada_import(filepath=fname, import_units=True, auto_connect=False)
  bpy.ops.object.select_all(action='SELECT')
  objs = bpy.context.selected_objects
  cameraLocation = Vector((+0.0,0,+9.3)) #passage
  for obj in objs:
    if "O1" in obj.name:
      bpy.context.scene.frame_set(0)
      obj.rotation_mode = 'QUATERNION'
      obj.rotation_quaternion = [1,0,0,0]
      obj.keyframe_insert(data_path="rotation_quaternion", index=-1)

  for obj in objs:
    if "body" in obj.name:
      bpy.ops.object.select_all(action='DESELECT')
      obj.select_set(True)
      bpy.ops.object.delete() 
      break

if "sphere" in folder:
  cameraLocation = Vector((+5,0,+2))

  lightLocation = Vector((8,0,0))
  addLightSourcePoint(lightLocation)

  name = "spherespace"
  sphere_mesh = bpy.data.meshes.new(name)
  sphere_obj = bpy.data.objects.new(name, sphere_mesh)
  bpy.context.collection.objects.link(sphere_obj)

  ## select active object
  bpy.context.view_layer.objects.active = sphere_obj
  sphere_obj.select_set(True)

  ## add mesh
  bm = bmesh.new()
  bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32,
      diameter=1.0)
  bm.to_mesh(sphere_mesh)
  bm.free()

  bpy.ops.object.modifier_add(type='SUBSURF')
  bpy.ops.object.shade_smooth()

  ## add color
  sphere_obj.active_material = materialWhiteTransparent

  #################################################################################
  #### PUNCTURING OF SPHERE
  #################################################################################
  sphere_obj.data.materials.append(materialWhiteTransparent)
  sphere_obj.show_transparent = True #  displays trans in viewport

  cutter = CuttingTools()
  cutter.CutSphericalHole(sphere_obj, location = Vector([1,0,0]), diameter=0.5)
  cutter.CutSphericalHole(sphere_obj, location = Vector([-1,0,0]), diameter=0.5)

if "multigoal" in folder:
  cameraLocation = Vector((+0.0,0,+11)) #passage
  sizeStates = 0.3

if "torus" in folder:
  cameraLocation = Vector((+6,0,+6)) #torus
  torusMajorRadius = 1
  torusMinorRadius = 0.6
  torus_mesh = bpy.ops.mesh.primitive_torus_add(major_radius = torusMajorRadius,
      minor_radius = torusMinorRadius,
      major_segments = 64, minor_segments = 32, location=(0,0,0))
  torus_obj = bpy.context.object
  torus_obj.name = 'Torus'

  #################################################################################
  #### PUNCTURING OF TORUS
  #################################################################################
  torus_obj.data.materials.append(materialWhiteTransparent)
  torus_obj.show_transparent = True #  displays trans in viewport

  ### DELETE INNER VERTICES
  cutter = CuttingTools()
  cutter.CutSphericalHole(torus_obj, location = Vector([0,1,0.5]), diameter=0.5)

########################################################
### SET START/GOAL
########################################################
# setBackgroundColor([1,1,1])
# array = PathArray(folder)

# startState = array.getStartState()
# startState = Vector([startState[0],startState[1],startState[2]])
# addSphere(startState, "startState", color=colorStartState, size=sizeStates)

# goalStates = array.getGoalStates()
# for goalState in goalStates:
#   goalState = Vector([goalState[0],goalState[1],goalState[2]])
#   addSphere(goalState, "goalState", color=colorGoalState, size=sizeStates)

################################################################################
### LIGHTNING & CAMERA
################################################################################
lightLocation = 0.3*(cameraLocation-cameraFocusPoint)+Vector((0,0,+5))
addLightSourcePoint(lightLocation)

camera = Camera(cameraLocation, cameraFocusPoint)

################################################################################
### RENDERING
################################################################################
bpy.context.scene.frame_end += 100

render = RenderEngine(folder)

# render.LastFrameToPNG(filename = dirname+"/"+filename+'.png')

elapsed_time = time.process_time() - time_start_script
print("TIME for RENDERING: %f (in s), %f (in m), %f (in h)"%\
    (elapsed_time,elapsed_time/60,elapsed_time/60/60))

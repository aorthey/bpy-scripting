import bpy
import bmesh

import numpy as np
import sys, os 
import re
import time
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

from bpy_utils import *
from Anim import *
from Camera import *
from src.Path import Path
from src.PathArray import PathArray
from src.Colors import materialMagenta
from src.RenderEngine import RenderEngine

#[ ] automate camera selection for each scenario

time_start_script = time.process_time()

cameraLocation = Vector((+6,0,+6)) #torus
cameraFocusPoint = Vector((0,0,0))

sizeStates = 0.15
renderAnimation=False
renderImage=False
folder = "data/modes/passage/"
folder = "data/modes/torus/"
folder = "data/modes/sphere/"
folder = "data/modes/multigoal/"
folder = "data/modes/lattice/"
folder = "data/modes/rod/"
folder = "data/modes/jaillet/"

filename = os.path.basename(os.path.dirname(folder))

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

########################################################
## DEFINE COLORS
########################################################
torusMaterial = bpy.data.materials.new(name="Gray")
torusMaterial.diffuse_color = (0.9, 0.9, 0.9, 1.0)
torusMaterial.metallic = 0.3
torusMaterial.specular_intensity = 0.9

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

      torusMaterial.use_nodes=True
      nodes = torusMaterial.node_tree.nodes
      for node in nodes:
          nodes.remove(node)
      links = torusMaterial.node_tree.links

      node_output  = nodes.new(type='ShaderNodeOutputMaterial')
      node_output.location = 400,0
      node_pbsdf    = nodes.new(type='ShaderNodeBsdfPrincipled')
      node_pbsdf.location = 0,0
      node_pbsdf.inputs['Base Color'].default_value = torusMaterial.diffuse_color
      node_pbsdf.inputs['Alpha'].default_value = 0.4 # 1 is opaque, 0 is invisible
      node_pbsdf.inputs['Roughness'].default_value = 0.1
      node_pbsdf.inputs['Specular'].default_value = 0.5
      node_pbsdf.inputs['Transmission'].default_value = 0.7 # 1 is fully transparent

      link = links.new(node_pbsdf.outputs['BSDF'], node_output.inputs['Surface'])

      torusMaterial.blend_method = 'HASHED'
      torusMaterial.shadow_method = 'HASHED'
      torusMaterial.use_screen_refraction = True
      addMaterialToObject(obj, torusMaterial)

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
  sphere_obj.active_material = torusMaterial

  #################################################################################
  #### PUNCTURING OF SPHERE
  #################################################################################
  sphere_obj.data.materials.append(torusMaterial)
  sphere_obj.show_transparent = True #  displays trans in viewport

  bpy.ops.object.modifier_add(type='SUBSURF')
  bpy.ops.object.shade_smooth()

  bpy.ops.object.select_all(action='DESELECT')

  mesh = bpy.data.meshes.new('Basic_Sphere')
  basic_sphere = bpy.data.objects.new("Basic_Sphere", mesh)
  basic_sphere.location = basic_sphere.location + Vector([-1,0,0])
  bpy.context.collection.objects.link(basic_sphere)
  bpy.context.view_layer.objects.active = basic_sphere
  basic_sphere.select_set(True)
  bm = bmesh.new()
  bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=0.5)
  bm.to_mesh(mesh)
  bm.free()

  mesh = bpy.data.meshes.new('Basic_Sphere2')
  basic_sphere_two = bpy.data.objects.new("Basic_Sphere2", mesh)
  basic_sphere_two.location = basic_sphere_two.location + Vector([+1,0,0])
  bpy.context.collection.objects.link(basic_sphere_two)
  bpy.context.view_layer.objects.active = basic_sphere_two
  basic_sphere_two.select_set(True)
  bm = bmesh.new()
  bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=0.5)
  bm.to_mesh(mesh)
  bm.free()

  # torus_obj.select_set(True)
  bpy.context.view_layer.objects.active = sphere_obj

  bool_mod = sphere_obj.modifiers.new(type="BOOLEAN", name="bool1")
  bool_mod.operation = 'DIFFERENCE'
  bool_mod.object = basic_sphere
  bpy.ops.object.modifier_apply(modifier=bool_mod.name)

  bool_mod = sphere_obj.modifiers.new(type="BOOLEAN", name="bool2")
  bool_mod.operation = 'DIFFERENCE'
  bool_mod.object = basic_sphere_two
  bpy.ops.object.modifier_apply(modifier=bool_mod.name)

  bpy.ops.object.select_all(action='DESELECT')
  basic_sphere.select_set(True)
  bpy.ops.object.delete() 
  basic_sphere_two.select_set(True)
  bpy.ops.object.delete() 

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

  torusMaterial.use_nodes=True
  nodes = torusMaterial.node_tree.nodes
  for node in nodes:
      nodes.remove(node)
  links = torusMaterial.node_tree.links

  node_output  = nodes.new(type='ShaderNodeOutputMaterial')
  node_output.location = 400,0
  node_pbsdf    = nodes.new(type='ShaderNodeBsdfPrincipled')
  node_pbsdf.location = 0,0
  node_pbsdf.inputs['Base Color'].default_value = torusMaterial.diffuse_color
  node_pbsdf.inputs['Alpha'].default_value = 0.3 # 1 is opaque, 0 is invisible
  node_pbsdf.inputs['Roughness'].default_value = 0.2
  node_pbsdf.inputs['Specular'].default_value = 0.9
  node_pbsdf.inputs['Transmission'].default_value = 0.5 # 1 is fully transparent

  link = links.new(node_pbsdf.outputs['BSDF'], node_output.inputs['Surface'])

  torusMaterial.blend_method = 'HASHED'
  torusMaterial.shadow_method = 'HASHED'
  torusMaterial.use_screen_refraction = True

  #################################################################################
  #### PUNCTURING OF TORUS
  #################################################################################
  torus_obj.data.materials.append(torusMaterial)
  torus_obj.show_transparent = True #  displays trans in viewport

  bpy.ops.object.modifier_add(type='SUBSURF')
  bpy.ops.object.shade_smooth()


  bpy.ops.object.select_all(action='DESELECT')

  mesh = bpy.data.meshes.new('Basic_Sphere')
  basic_sphere = bpy.data.objects.new("Basic_Sphere", mesh)
  basic_sphere.location = basic_sphere.location + Vector([0,1,0.5])

  bpy.context.collection.objects.link(basic_sphere)
  bpy.context.view_layer.objects.active = basic_sphere
  basic_sphere.select_set(True)
  bm = bmesh.new()
  bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=0.5)
  bm.to_mesh(mesh)
  bm.free()

  # torus_obj.select_set(True)
  bpy.context.view_layer.objects.active = torus_obj

  bool_mod = torus_obj.modifiers.new(type="BOOLEAN", name="bool1")
  bool_mod.operation = 'DIFFERENCE'
  bool_mod.object = basic_sphere

  bpy.ops.object.modifier_apply(modifier=bool_mod.name)

  bpy.ops.object.select_all(action='DESELECT')
  basic_sphere.select_set(True)
  bpy.ops.object.delete() 

########################################################
### SET START/GOAL
########################################################
setBackgroundColor([1,1,1])
array = PathArray(folder)

startState = array.getStartState()
startState = Vector([startState[0],startState[1],startState[2]])
addSphere(startState, "startState", color=colorStartState, size=sizeStates)

goalStates = array.getGoalStates()
for goalState in goalStates:
  goalState = Vector([goalState[0],goalState[1],goalState[2]])
  addSphere(goalState, "goalState", color=colorGoalState, size=sizeStates)

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

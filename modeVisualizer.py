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
from src.Colors import materialMagenta

cameraLocation = Vector((+6,0,+6))
cameraFocusPoint = Vector((0,0,0))
sizeStates = 0.15
folder = "data/modes/torus/"
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

curveMaterial = bpy.data.materials.new(name="Curve")
curveMaterial.diffuse_color = (0.08, 0.7, 0.08, 1.0)
curveMaterial.diffuse_color = (0.9, 0.01, 0.01, 1.0)
curveMaterial.metallic = 0.7
curveMaterial.specular_intensity = 0.9
fname = os.path.abspath(dirname+"/" + folder + "scene.dae")

# c = bpy.ops.wm.collada_import(filepath=fname, import_units=True, auto_connect=False)

curves = {}
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = 0

########################################################
### LOAD CURVES
########################################################
PathArray = []
for filename in os.listdir(folder):
  if not filename.endswith(".path"):
    continue
  path = Path(folder+"/"+filename)
  PathArray.append(path)

for path in PathArray:
  print(path.name,":",len(path.keyframes)," ",path.timeStart," ",path.timeEnd)

  curve = addBezierCurve(path.name, N=path.Nstates-1)
  curve.data.materials.clear()
  curve.data.materials.append(curveMaterial)
  curve.show_transparent = True

  curves[path.name] = curve

  curve.hide_render = True
  curve.keyframe_insert(data_path="hide_render", frame=0)
  curve.hide_viewport = True
  curve.keyframe_insert("hide_viewport", frame=0)

  curve.hide_render = False
  curve.keyframe_insert(data_path="hide_render", frame=path.timeStart)
  curve.hide_viewport = False
  curve.keyframe_insert("hide_viewport", frame=path.timeStart)

  if path.to_be_removed:
    curve.hide_render = True
    curve.keyframe_insert(data_path="hide_render", frame=path.removal_time)
    curve.hide_viewport = True
    curve.keyframe_insert("hide_viewport", frame=path.removal_time)

  for keyframe in path.keyframes:
    if keyframe.time > bpy.context.scene.frame_end:
      bpy.context.scene.frame_end = keyframe.time

    bpy.context.scene.frame_set(keyframe.time)
    P = curve.data.splines[0].points
    for (index, state) in enumerate(keyframe.states):
      p = P[index]
      p.co= (state[0], state[1], state[2], 1)
      p.keyframe_insert(data_path="co")

startState = PathArray[0].keyframes[0].states[0]
goalState = PathArray[0].keyframes[0].states[-1]

startState = Vector([startState[0],startState[1],startState[2]])
goalState = Vector([goalState[0],goalState[1],goalState[2]])

addSphere(startState, "startState", color=colorStartState, size=sizeStates)
addSphere(goalState, "goalState", color=colorGoalState, size=sizeStates)
########################################################
### ADD TORUS
########################################################

torusMajorRadius = 1
torusMinorRadius = 0.6
torus_mesh = bpy.ops.mesh.primitive_torus_add(major_radius = torusMajorRadius,
    minor_radius = torusMinorRadius,
    major_segments = 64, minor_segments = 32, location=(0,0,0))
torus_obj = bpy.context.object
torus_obj.name = 'Torus'


################ Additional transparency
torusMaterial.use_nodes=True
nodes = torusMaterial.node_tree.nodes
    # clear all nodes to start clean
for node in nodes:
    nodes.remove(node)
    # link nodes
links = torusMaterial.node_tree.links

    #create the basic material nodes
node_output  = nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = 400,0
node_pbsdf    = nodes.new(type='ShaderNodeBsdfPrincipled')
node_pbsdf.location = 0,0
node_pbsdf.inputs['Base Color'].default_value = torusMaterial.diffuse_color
node_pbsdf.inputs['Alpha'].default_value = 0.5 # 1 is opaque, 0 is invisible
node_pbsdf.inputs['Roughness'].default_value = 0.2
node_pbsdf.inputs['Specular'].default_value = 0.9
node_pbsdf.inputs['Transmission'].default_value = 0.5 # 1 is fully transparent

link = links.new(node_pbsdf.outputs['BSDF'], node_output.inputs['Surface'])

torusMaterial.blend_method = 'HASHED'
torusMaterial.shadow_method = 'HASHED'
torusMaterial.use_screen_refraction = True

torus_obj.data.materials.append(torusMaterial)
torus_obj.show_transparent = True #  displays trans in viewport

bpy.ops.object.modifier_add(type='SUBSURF')
bpy.ops.object.shade_smooth()



################################################################################
### PUNCTURING OF TORUS
################################################################################

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

################################################################################
### LIGHTNING & CAMERA
################################################################################
lightLocation = 0.3*(cameraLocation-cameraFocusPoint)+Vector((0,0,+5))
addLightSourcePoint(lightLocation)

camera = Camera(cameraLocation, cameraFocusPoint)

################################################################################
### RENDERING
################################################################################

bpy.context.scene.eevee.use_ssr = True
bpy.context.scene.eevee.use_ssr_refraction = True

#### VIDEO (MP4)
renderEngine = bpy.context.scene.render
renderEngine.image_settings.file_format = "FFMPEG"
renderEngine.ffmpeg.format = "MPEG4"
renderEngine.ffmpeg.codec = "H264"
renderEngine.ffmpeg.constant_rate_factor = "HIGH" #MEDIUM, LOW
renderEngine.filepath = dirname+"/"+filename+".mp4"

#### IMAGE (PNG)
# renderEngine = bpy.context.scene.render
# renderEngine.film_transparent = True
# renderEngine.image_settings.file_format = "PNG"
# renderEngine.image_settings.color_mode = 'RGBA'
# renderEngine.filepath = dirname+"/"+filename+'.png'
# bpy.ops.render.render(write_still = True)

# renderEngine.filepath = dirname+"/"+filename+'.png'
# ff = renderEngine.filepath
# os.system("convert -trim %s %s"%(ff,ff))
# print(renderEngine.filepath)


### Render Animation to MP4 video
# if renderAnimation:
#   print("Starting to render %d frames."% bpy.context.scene.frame_end)
#   bpy.ops.render.render(animation=True)

# elapsed_time = time.process_time() - time_start_script
# print("TIME for RENDERING: %f (in s), %f (in m), %f (in h)"%\
#     (elapsed_time,elapsed_time/60,elapsed_time/60/60))

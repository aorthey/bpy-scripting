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
NkeyframeSteps = 10 #use every n-th keyframe, interpolate inbetween
renderAnimation = False
########################################################

cameraLocation = Vector((+3,-9,+5))
cameraFocusPoint = Vector((0,0,0))

fname = os.path.abspath(dirname+"/data/initial.dae")

## delete all previous objects in scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

c = bpy.ops.wm.collada_import(filepath=fname, import_units=True,
    auto_connect=False)

## SELECT ALL OBJECTS IN BLENDER
bpy.ops.object.select_all(action='SELECT')

objs = bpy.context.selected_objects

A = Anim("data/Anim.txt")
for obj in objs:
  if obj.name == "plate":
    bpy.context.scene.frame_set(0)
    obj.location = [0,0,0]
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
    print("Importing segment %d/%d (link %d/%d)"%(ctr,len(A.segments),n,len(segment.names)))
    for obj in bpy.context.selected_objects:
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

filename = "animation"

## NOTE: need to rotate camera
# direction = cameraFocusPoint - cameraLocation
# rot_quat = direction.to_track_quat('-Z', 'Y')
# rot_quat = rot_quat.to_matrix().to_4x4()

# cameraLocation = cameraLocation.to_tuple()

# roll = radians(90)
# camera_roll = Matrix.Rotation(roll, 4, 'Z')
# bpy.context.scene.camera.matrix_world = rot_quat @ camera_roll
# bpy.context.scene.camera.location = cameraLocation

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
# if renderAnimation:
#   bpy.ops.render.render(animation=True)

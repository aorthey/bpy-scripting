import bpy
import bmesh
import numpy as np
import sys, os 
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

from bpy_utils import *
from Anim import *

# cameraLocation = Vector((+3,-1.5,+2.5))
# cameraFocusPoint = Vector((0,0,0))
cameraLocation = Vector((+15,-15,0))
cameraFocusPoint = Vector((0,0,0))

fname = os.path.abspath(dirname+"/data/initial.dae")

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

c = bpy.ops.wm.collada_import(filepath=fname, import_units=True)

## SELECT ALL OBJECTS IN BLENDER
bpy.ops.object.select_all(action='SELECT')

A = Anim("/data/Anim.txt")

sk = A.segments[0]
for segment in A.segments:
  for n in range(0,len(segment.names)):
    name = segment.names[n]
    for obj in bpy.context.selected_objects:
      if obj.name == name:
        ## FOUND match between collada object and Anim object for current segment
        print(obj.name)
        for t in range(segment.timeStart, segment.timeEnd):
          pose = segment.getPoses(t, name)
          bpy.context.scene.frame_set(t)
          obj.location = pose[0:3]
          obj.rotation_mode = 'QUATERNION'
          obj.rotation_quaternion = pose[3:]
          # obj.location = pose
          obj.keyframe_insert(data_path="location", index=-1)
          obj.keyframe_insert(data_path="rotation_quaternion", index=-1)

filename = "animation"

addCamera(cameraLocation, cameraFocusPoint)
## NOTE: need to rotate camera
direction = cameraFocusPoint - cameraLocation
rot_quat = direction.to_track_quat('-Z', 'Y')
rot_quat = rot_quat.to_matrix().to_4x4()

cameraLocation = cameraLocation.to_tuple()

roll = radians(90)  # select your desired amount of
camera_roll = Matrix.Rotation(roll, 4, 'Z')
bpy.context.scene.camera.matrix_world = rot_quat @ camera_roll
bpy.context.scene.camera.location = cameraLocation

addLightSourceSun(Vector((-10,0,2)))
addLightSourceSun(Vector((+10,0,2)))
addLightSourceSun(Vector((0,+10,2)))
addLightSourceSun(Vector((0,-10,2)))
addLightSourceSun(Vector((0,0,+10)))


### RENDERING 
# bpy.context.scene.render.film_transparent = True
# bpy.context.scene.render.image_settings.color_mode = 'RGBA'

# bpy.context.scene.render.filepath = dirname+"/"+filename+'.png'

# bpy.ops.render.render(write_still = True)

# ff = bpy.context.scene.render.filepath
# os.system("convert -trim %s %s"%(ff,ff))

# print(bpy.context.scene.render.filepath)


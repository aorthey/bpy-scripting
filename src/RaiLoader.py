import bpy
import numpy as np
import sys, os 
import re
from xml.dom.minidom import parse
from src.RaiAnim import *
from src.Utils import *

class RaiLoader():

  def __init__(self, foldername):

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    fname = os.path.abspath(foldername + "initial.dae")
    print(fname)
    self.anim = Anim(foldername + "Anim.txt")

    c = bpy.ops.wm.collada_import(filepath=fname, import_units=True, auto_connect=False)

    bpy.ops.object.select_all(action='SELECT')

    objs = bpy.context.selected_objects

    self.curves = {}
    for obj in objs:
      if "gripper" in obj.name:
        curveDynamic = addBezierCurve(obj.name)
        self.curves[obj.name] = curveDynamic
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

  def generateKeyframesFromAnim(self, Nsegments = -1, NkeyframeSteps=1):
    A = self.anim
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
              P = self.curves[obj.name].data.splines[0].points
              addMaterialColor(self.curves[obj.name], color)
              material = self.curves[obj.name].active_material
              material.shadow_method = 'NONE'
              self.curves[obj.name].cycles_visibility.shadow = False
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
                slot = self.curves[obj.name].material_slots[0]
                slot.material.diffuse_color[3] = alpha

                p.keyframe_insert(data_path="co", index=-1)

          ####WEIRD behavior during fadeout
          if "gripper" in obj.name:
            ##add fadeout
            tend = segment.timeEnd

            P = self.curves[obj.name].data.splines[0].points
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


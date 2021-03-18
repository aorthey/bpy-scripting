import bpy
import numpy as np
import sys, os 
from src.Path import Path

curveMaterial = bpy.data.materials.new(name="Curve")
curveMaterial.diffuse_color = (0.08, 0.7, 0.08, 1.0)
curveMaterial.diffuse_color = (0.9, 0.01, 0.01, 1.0)
curveMaterial.metallic = 0.7
curveMaterial.specular_intensity = 0.9
curveMaterial.shadow_method = 'NONE'

class PathArray():

  def __init__(self, folder):
    self.array = []
    self.curves = {}

    for filename in os.listdir(folder):
      if not filename.endswith(".path"):
        continue
      path = Path(folder+"/"+filename)
      self.array.append(path)

    for path in self.array:
      print(path.name,":",len(path.keyframes)," ",path.timeStart," ",path.timeEnd)

      curve = self.addBezierCurve(path.name, N=path.Nstates-1)
      curve.data.materials.clear()
      curve.data.materials.append(curveMaterial)
      curve.show_transparent = True

      self.curves[path.name] = curve

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

  def addBezierCurve(self, name, N, thickness=0.02):
    curve = bpy.data.curves.new(name="Mode"+name, type='CURVE')
    curve.dimensions = '3D'
    curveObject = bpy.data.objects.new("path", curve)
    curveObject.location = (0,0,0)

    ### create milestones
    polyline = curve.splines.new('POLY')

    polyline.points.add(N)
    for p in polyline.points:
      p.co = (0, 0, 0, 1)

    bpy.context.collection.objects.link(curveObject)

    curve.fill_mode = 'FULL'
    curve.bevel_depth = thickness

    curveObject.data.materials.append(curveMaterial)
    curveObject.show_transparent = True
    return curveObject

  def getStartState(self):
    if len(self.array)>0:
      return self.array[0].keyframes[0].states[0]

  def getGoalStates(self):
    # states = []
    states = np.empty((0,3), float)
    for path in self.array:
      state = np.array(path.keyframes[0].states[-1])
      state = np.array([[state[0],state[1],state[2]]])
      states = np.append(states, np.array(state), axis=0)

    states = np.vstack(list({tuple(row) for row in states}))
    print("Found ",len(states),"goal states.")
    return states

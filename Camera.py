import bpy
import numpy as np
import copy
from mathutils import *


def spherical_to_cartesian(r,theta,phi):
  x = r*np.sin(theta)*np.cos(phi)
  y = r*np.sin(theta)*np.sin(phi)
  z = r*np.cos(theta)
  return(x,y,z)

def cartesian_to_spherical(x,y,z):
  r = np.sqrt(x**2 + y**2 + z**2)
  theta = np.arccos(z/r)
  phi = np.arctan2(y,x)
  return(r,theta,phi)

class Camera():
  cam = []
  cam_object = []
  focus = []
  location = []
  distance = 0
  distanceBeginning = 0

  def __init__(self, location, focus):
    self.location = location
    self.focus = focus
    self.distance = self.getVectorNorm(self.location - self.focus)
    self.distanceBeginning = self.distance

    self.cam = bpy.data.cameras.new("Camera")
    self.cam_object = bpy.data.objects.new("Camera", self.cam)
    bpy.context.collection.objects.link(self.cam_object)
    self.cam_object.location = self.location
    bpy.context.scene.camera = self.cam_object
    bpy.context.view_layer.objects.active = self.cam_object

    # constraint = self.cam_object.constraints.new("TRACK_TO")
    # constraint.target = Vector((focus[0], focus[1], focus[2]))
    # constraint.track_axis = "TRACK_NEGATIVE_Z"
    # constraint.up_axis = "UP_Y"
    self.update_camera(self.cam_object, focus_point=self.focus)

  def update_camera(self, camera, focus_point=Vector((0.0, 0.0, 0.0))):
      looking_direction = camera.location - focus_point
      rot_quat = looking_direction.to_track_quat('Z', 'Y')
      distance = self.getVectorNorm(looking_direction)

      camera.rotation_mode = 'XYZ'
      camera.rotation_euler = rot_quat.to_euler()
      # camera.location = camera.location# + rot_quat @ Vector((0.0, 0.0, distance))

		# dx = focus_point - camera.location
    # # Signs are chosen carefully due to geometry.  If we rotate
    # #  by this much from the -z orientation around the x-axis, we
    # #  will be pointing along the y-axis (for angle &lt; pi rad)
    # xRad = (3.14159/2.) + math.atan2(dz, math.sqrt(dy**2 + dx**2))
    # print("xRad: %f, %f deg" % (xRad, xRad*180./math.pi))
    
    # zRad = math.atan2(dy, dx) - (3.14159256 / 2.)
    # print("zRad: %f, %f deg" % (zRad, zRad*180./math.pi))
    # cam.rotation_euler = mathutils.Euler((xRad, 0, zRad), 'XYZ')


  def getVectorNorm(self, v):
    n = v.dot(v)
    return np.sqrt(n)

  def zoomIn(self, timeStart, timeEnd, dend_percentage = 0.7):
    bpy.context.view_layer.objects.active = self.cam_object

    T = timeEnd - timeStart

    p0 = copy.copy(self.cam_object.location)
    p1 = self.focus
    dp = p1 - p0
    d = self.getVectorNorm(dp)
    dpn = dp / d

    for t in range(timeStart, timeEnd):
      bpy.context.scene.frame_set(t)

      tcur = t - timeStart
      tstep = tcur / T

      #from d to dend * d
      dt = tstep * (dend_percentage * d)
      dv = dpn * dt

      self.cam_object.location = p0 + dv
      self.update_camera(self.cam_object, focus_point=self.focus)

      self.cam_object.keyframe_insert(data_path="location", index=-1)
      self.cam_object.keyframe_insert(data_path="rotation_euler", index=-1)

  def zoomOut(self, timeStart, timeEnd, dstep = 0.4):
    bpy.context.view_layer.objects.active = self.cam_object

    T = timeEnd - timeStart

    p0 = self.cam_object.location
    p1 = self.focus
    dp = p1 - p0
    d = self.getVectorNorm(dp)

    dv = dstep * (dp / d)

    for t in range(timeStart, timeEnd):
      bpy.context.scene.frame_set(t)

      p0 = self.cam_object.location

      # tcur = t - timeStart
      # tstep = tcur / T

      # dt = - tstep * (dend_percentage * d)
      # dv = dpn * dt

      self.cam_object.location = p0 - dv
      self.update_camera(self.cam_object, focus_point=self.focus)
      self.cam_object.keyframe_insert(data_path="location", index=-1)
      self.cam_object.keyframe_insert(data_path="rotation_euler", index=-1)


  def rotate(self, timeStart, timeEnd, velocity = 0.01):
    bpy.context.view_layer.objects.active = self.cam_object

    T = timeEnd - timeStart

    # bpy.context.scene.frame_set(timeStart)

    # phiUpdate = phi

    for t in range(timeStart, timeEnd):
      bpy.context.scene.frame_set(t)
      p0 = self.cam_object.location
      [R, theta, phi] = cartesian_to_spherical(p0[0], p0[1], p0[2])

      tcur = t - timeStart
      tstep = tcur / T
      phiUpdate = phi + 0.002*2*np.pi

      [x,y,z] = spherical_to_cartesian(R, theta, phiUpdate)

      p = Vector((x,y,z))

      self.cam_object.location = p

      self.update_camera(self.cam_object, focus_point=self.focus)

      # print(t, phi, self.cam_object.location, self.cam_object.rotation_euler)

      self.cam_object.keyframe_insert(data_path="location", index=-1)
      self.cam_object.keyframe_insert(data_path="rotation_euler", index=-1)
    return


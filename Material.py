import bpy
import bmesh
import numpy as np
from math import *
from mathutils import *

class Material():
  material = []

  def __init__(self, filename):
    self.material = bpy.data.materials.new(name="Texture")
    # materialTexture.diffuse_color = (1.0, 1.0, 1.0, 1.0)
    self.material.metallic = 0.0
    self.material.specular_intensity = 0.0
    self.material.use_nodes = True
    bsdf = self.material.node_tree.nodes["Principled BSDF"]
    texImage = self.material.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(filename)
    self.material.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

class MaterialColor():
  material = []

  def __init__(self, color):
    self.material = bpy.data.materials.new(name="Green")
    self.material.diffuse_color = (color[0],color[1],color[2],color[3])
    self.material.metallic = 0.0
    self.material.specular_intensity = 0.0

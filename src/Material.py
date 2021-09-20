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

class MaterialGlass():
  material = []

  def __init__(self):
    name = 'planeGlass'
    self.material = bpy.data.materials.new(name)
    # bpy.ops.mesh.primitive_plane_add()
    # bpy.data.materials[name].use_nodes = True
    # shader = bpy.data.materials[name].node_tree.nodes.new(type='ShaderNodeBsdfGlass')
    # shader.inputs['Roughness'].default_value = 0.5
    # shader.inputs['IOR'].default_value = 10
    # # shader.inputs['Color'].default_value = (0.35,0.44,1.0)

    # inp = bpy.data.materials[name].node_tree.nodes['Material Output'].inputs['Surface']
    # outp = bpy.data.materials[name].node_tree.nodes['Glass BSDF'].outputs['BSDF']

    # bpy.data.materials[name].node_tree.nodes['Glass BSDF'].inputs[2].default_value = 10.0

    self.material.diffuse_color = (0.35, 0.44, 1.0, 1.0)
    self.material.roughness = 0.4

class MaterialColor():
  material = []

  def __init__(self, color):
    self.material = bpy.data.materials.new(name="Green")
    self.material.diffuse_color = (color[0],color[1],color[2],color[3])
    self.material.metallic = 0.3
    self.material.specular_intensity = 0.0

glass = MaterialGlass()
def addMaterialGlass(obj):
  return addMaterialToObject(obj, glass.material)

def addMaterialToObject(obj, material):
  if obj.data.materials:
      obj.data.materials[0] = material
  else:
      obj.data.materials.append(material)
  obj.active_material = material

def addMaterialColor(obj, color):
  if obj is None or obj.data is None:
    return
  material = MaterialColor(color).material
  addMaterialToObject(obj, material)


import bpy
import bmesh
from src.Colors import materialGrey

class CuttingTools():
  def ColorDifference(self, obj):
    ##############################################
    ### COLOR INNER FACES
    ### NOTE: the trick here is that the boolean difference operator created new
    ### vertices on our bottle. However, those new vertices are not yet selected. We
    ### therefore can go to edit mode, do an inverse selection (to select all new
    ### vertices) and then delete them OR color them.
    ##############################################
    bpy.ops.object.mode_set(mode = 'OBJECT')

    bpy.ops.object.mode_set(mode = 'EDIT') 
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action='INVERT')

    for face in obj.data.polygons:
      if face.select:
        face.material_index = len(obj.data.materials)-1

    # bpy.ops.mesh.select_mode(type="VERT")
    # bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

  def CutSphericalHole(self, obj_to_cut, location, diameter):
    materialForFilling = materialGrey
    obj_to_cut.data.materials.append(materialForFilling)
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.ops.object.shade_smooth()

    bpy.ops.object.select_all(action='DESELECT') 
    mesh = bpy.data.meshes.new('Basic_Sphere')
    basic_sphere = bpy.data.objects.new("Basic_Sphere", mesh)
    basic_sphere.location = basic_sphere.location + location
    basic_sphere.data.materials.append(materialForFilling)

    bpy.context.collection.objects.link(basic_sphere)
    bpy.context.view_layer.objects.active = basic_sphere
    basic_sphere.select_set(True)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, diameter=diameter)
    bm.to_mesh(mesh)
    bm.free()

    bpy.context.view_layer.objects.active = obj_to_cut

    bool_mod = obj_to_cut.modifiers.new(type="BOOLEAN", name="bool1")
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = basic_sphere

    bpy.ops.object.modifier_apply(modifier=bool_mod.name)

    bpy.ops.object.select_all(action='DESELECT')
    basic_sphere.select_set(True)
    bpy.ops.object.delete() 

    self.ColorDifference(obj_to_cut)

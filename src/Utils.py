import bpy
import bmesh
import numpy as np
from math import *
from mathutils import *

from src.Material import *

distanceCamera = 35
cameraFocusPoint = Vector((0,-8,-7))
offsetAnnulusLeft = Vector((-3, +1, -15))
offsetAnnulusRight = Vector((-3,-15, -15))
torusMinorRadius = 2
torusMajorRadius = 3.5
torusLocation = (0,0,0)

colorStartState = (0.0, 1.0, 0.0, 1.0)
colorGoalState = (0.7, 0.0, 0.0, 1.0)

diameterState = 0.15
mobiusStripThickness = 0.1
pathThickness = 0.3
circleThickness = 0.3
minor_radius = 2
major_radius = 5

materialGreen = bpy.data.materials.new(name="Green")
materialGreen.diffuse_color = (0.0, 1.0, 0.0, 1.0)
materialGreen.metallic = 0.0
materialGreen.specular_intensity = 0.0

purplePosy = (236/256.0, 223/256.0, 237/256.0, 1.0)
rococoRose = (221/256.0, 146/256.0, 155/256.0, 1.0)
seasideSpray = (183/256.0, 204/256.0, 226/256.0, 1.0)

blushingBride = (249/256.0, 194/256.0, 188/256.0, 1.0) #cherry red
calypsoCoral = (241/256.0, 116/256.0, 91/256.0, 1.0) #calypso red
petalPink = (252/256.0, 206/256.0, 182/256.0, 1.0) #pink-ish
soSaflron = (255/256.0, 218/256.0, 141/256.0, 1.0) #yellow-ish
softSeaFoam = (234/256.0, 241/256.0, 213/256.0, 1.0) #soft green-ish
pearPizzazz = (184/256.0, 192/256.0, 104/256.0, 1.0) #dark green-ish
mintMacaron = (159/256.0, 197/256.0, 170/256.0, 1.0) #mint-ish
poolParty = (171/256.0, 217/256.0, 213/256.0, 1.0) #aqua green-ish
balmyBlue = (169/256.0, 214/256.0, 235/256.0, 1.0) #blue-ish
highlandHeather = (173/256.0, 153/256.0, 200/256.0, 1.0)  #magenta-ish

##https://machsdirschoen.info/wp-content/uploads/2019/05/Stampin-Up-Farbencodes-RGB-HEX-05_2019.pdf
materialRose = bpy.data.materials.new(name="RococoRose")
materialRose.diffuse_color = blushingBride
materialRose.metallic = 0.0
materialRose.specular_intensity = 0.1

materialMagenta = bpy.data.materials.new(name="Magenta")
materialMagenta.diffuse_color = (0.205, 0.0, 0.37, 1.0)
materialMagenta.metallic = 0.9
materialMagenta.specular_intensity = 0.9
# materialMagenta.blend_method = "BLEND"
# materialMagenta.use_transparency = True #  renders trans

def getVectorNorm(v):
  n = v.dot(v)
  return np.sqrt(n)

def arrow_mesh(position, length, width=-1, headlength=-1, headwidth = -1):
    verts = []
    faces = []

    if width < 0:
      width = 0.15*length
    if headlength < 0:
      headlength = 0.3*length
    if headwidth < 0:
      headwidth = 2*width

    v1 = position
    v2 = Vector((position[0], position[1] - 0.5*headwidth, position[2] + headlength))
    v3 = Vector((position[0], position[1] - 0.5*width, position[2] + headlength))
    v4 = Vector((position[0], position[1] - 0.5*width, position[2] + length))

    v5 = Vector((position[0], position[1] + 0.5*headwidth, position[2] + headlength))
    v6 = Vector((position[0], position[1] + 0.5*width, position[2] + headlength))
    v7 = Vector((position[0], position[1] + 0.5*width, position[2] + length))


    #   3---6
    #   |   |
    #   |   |
    #1--2---5--4
    # \       /
    #  \     /
    #   \   /
    #    \ /
    #     0

    # verts.extend([v1, v2])
    verts.extend([v1, v2, v3, v4, v5, v6, v7])
    faces.append([0, 1, 2])
    faces.append([0, 2, 5])
    faces.append([0, 5, 4])
    faces.append([2, 3, 6])
    faces.append([2, 6, 5])

    mesh = bpy.data.meshes.new("arrow")
    mesh.from_pydata(verts, [], faces)

    for p in mesh.polygons:
        p.use_smooth=True

    return mesh


def annulus_mesh(resolution, inner_radius, outer_radius):
    verts = []
    faces = []

    for i in range(resolution):
        theta = 2*pi * i/resolution
        rot = Matrix.Rotation(theta, 3, [0,0,1])
        v1 = rot @ Vector([inner_radius, 0, 0])
        v2 = rot @ Vector([outer_radius, 0, 0])

        i1 = len(verts)
        verts.extend([v1,v2])

        if i+1<resolution:
            ia = i1+2
            ib = i1+3
        else:
            ia = 0
            ib = 1

        faces.append( [i1,i1+1,ib,ia])

    mesh = bpy.data.meshes.new("annulus")
    mesh.from_pydata(verts, [], faces)

    for p in mesh.polygons:
        p.use_smooth=True

    return mesh

def mobius_mesh(resolution, thick):

    verts = []
    faces = []

    for i in range(resolution):

        theta = 2*pi * i/resolution
        phi = pi * i/resolution

        rot1 = Matrix.Rotation(phi, 3, [0,1,0])
        rot2 = Matrix.Rotation(theta, 3, [0,0,1])
        c1 = Vector([major_radius, 0, 0])
        v1 = rot2 @ (c1 + rot1 @ Vector([-thick / 2, 0, minor_radius]) )
        v2 = rot2 @ (c1 + rot1 @ Vector([thick / 2, 0, minor_radius]) )
        v3 = rot2 @ (c1 + rot1 @ Vector([thick / 2, 0, -minor_radius]) )
        v4 = rot2 @ (c1 + rot1 @ Vector([-thick / 2, 0, -minor_radius]) )

        i1 = len(verts)
        verts.extend([v1,v2,v3,v4])

        if i+1<resolution:
            ia = i1+4
            ib = i1+5
            ic = i1+6
            id = i1+7
        else:
            ia = 2
            ib = 3
            ic = 0
            id = 1

        # faces.append( [i1+j for j in range(4) ])
        faces.append( [i1,i1+1,ib,ia])
        faces.append( [i1+1,i1+2,ic,ib])
        faces.append( [i1+2,i1+3,id,ic])
        faces.append( [i1+3,i1,ia,id])

    mesh = bpy.data.meshes.new("mobius")
    mesh.from_pydata(verts, [], faces)

    for p in mesh.polygons:
        p.use_smooth=True

    return mesh

def addPath():
    ## create curve OBJ
    curve = bpy.data.curves.new(name="L1FF", type='CURVE')
    curve.dimensions = '3D'
    path_obj = bpy.data.objects.new("path", curve)
    path_obj.location = (0,0,0)

    ### create milestones
    poly = curve.splines.new('POLY')
    X = np.arange(0.45,-0.01,-0.01)
    poly.points.add(2 + len(X) - 1)
    poly.points[0].co = getVectorOnStrip4D(0.45, 0.1)
    poly.points[1].co = getVectorOnStrip4D(0.45, 0.9)
    ctr = 2
    for x in X:
      poly.points[ctr].co = getVectorOnStrip4D(x, 0.9)
      ctr = ctr+1

    bpy.context.collection.objects.link(path_obj)

    curve.fill_mode = 'FULL'
    curve.bevel_depth = pathThickness

    path_obj.data.materials.append(materialGreen)


    # mesh = bpy.data.meshes.new("path_mesh")
    # mesh.from_pydata(verts, edges, [])

def addPathAnnulus():
    ## create curve OBJ
    curve = bpy.data.curves.new(name="PATH_ANNULUS", type='CURVE')
    curve.dimensions = '3D'
    path_obj = bpy.data.objects.new("path", curve)
    path_obj.location = (0,0,0)

    ### create milestones
    poly = curve.splines.new('POLY')
    X = np.arange(0.45,-0.01,-0.01)
    poly.points.add(len(X) - 1)
    ctr = 0
    for x in X:
      theta = x*(2*pi)
      rot = Matrix.Rotation(theta, 3, [0,0,1])
      v = (rot @ Vector([major_radius, 0, 0])) + offsetAnnulusLeft
      poly.points[ctr].co = (v[0],v[1],v[2],1)
      ctr = ctr+1

    bpy.context.collection.objects.link(path_obj)

    curve.fill_mode = 'FULL'
    curve.bevel_depth = pathThickness

    path_obj.data.materials.append(materialGreen)

def addPathTorusAnnulus():
    curve = bpy.data.curves.new(name="PATH_TORUS_ANNULUS", type='CURVE')
    curve.dimensions = '3D'
    path_obj = bpy.data.objects.new("path_torus_annulus", curve)
    path_obj.location = (0,0,0)

    ### create milestones
    poly = curve.splines.new('POLY')

    ## read X from file
    X = np.arange(0.55,0.85,+0.01)
    poly.points.add(len(X) - 1)
    ctr = 0
    for x in X:
      theta = x*(2*pi)
      rot = Matrix.Rotation(theta, 3, [0,0,1])
      v = (rot @ Vector([major_radius, 0, 0])) + offsetAnnulusRight
      poly.points[ctr].co = (v[0],v[1],v[2],1)
      ctr = ctr+1

    bpy.context.collection.objects.link(path_obj)

    curve.fill_mode = 'FULL'
    curve.bevel_depth = pathThickness

    path_obj.data.materials.append(materialGreen)

def update_camera(camera, focus_point=Vector((0.0, 0.0, 0.0)), distance=10.0):
    """
    Focus the camera to a focus point and place the camera at a specific distance from that
    focus point. The camera stays in a direct line with the focus point.

    :param camera: the camera object
    :type camera: bpy.types.object
    :param focus_point: the point to focus on (default=``Vector((0.0, 0.0, 0.0))``)
    :type focus_point: Vector
    :param distance: the distance to keep to the focus point (default=``10.0``)
    :type distance: float
    """
    looking_direction = camera.location - focus_point
    rot_quat = looking_direction.to_track_quat('Z', 'Y')

    camera.rotation_mode = 'XYZ'
    camera.rotation_euler = rot_quat.to_euler()
    camera.location = camera.location + rot_quat @ Vector((0.0, 0.0, distance))



def getVectorOnStrip4D(x_1, x_2):
    v = getVectorOnStrip(x_1, x_2)
    return (v[0],v[1],v[2],1)

def getVectorOnStrip(x_1, x_2):
    theta = x_1*(2*pi)
    phi = x_1*pi
    dx = -minor_radius+x_2*(2*minor_radius)

    rot1 = Matrix.Rotation(phi, 3, [0,1,0])
    rot2 = Matrix.Rotation(theta, 3, [0,0,1])
    c1 = Vector([major_radius, 0, 0])
    return rot2 @ (c1 + rot1 @ Vector([0, 0, dx]) )


def addSphere(pos, name, color=(1.0, 1.0, 1.0, 1.0), size=diameterState,
    u_segment=4, v_segment=2):
    xi_mesh = bpy.data.meshes.new(name)
    xi_obj = bpy.data.objects.new(name, xi_mesh)
    xi_obj.location = xi_obj.location + pos

    bpy.context.collection.objects.link(xi_obj)

    ## select active object
    bpy.context.view_layer.objects.active = xi_obj
    xi_obj.select_set(True)

    ## add mesh
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u_segment, v_segments=v_segment,
        diameter=size)
    bm.to_mesh(xi_mesh)
    bm.free()

    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.ops.object.shade_smooth()

    ## add color
    mat = bpy.data.materials.new("PKHG")
    mat.diffuse_color = color
    mat.metallic = 0.0
    mat.specular_intensity = 0.0
    xi_obj.active_material = mat


def addState(x_1, x_2, name, color=(1.0, 1.0, 1.0, 1.0)):

    pos = getVectorOnStrip(x_1, x_2)
    addSphere(pos, name, color)

def addStateAnnulusLeft(x_1, name, color=(1.0, 1.0, 1.0, 1.0)):
    addStateAnnulus(x_1, name, color, offsetAnnulusLeft)

def addStateAnnulusRight(x_1, name, color=(1.0, 1.0, 1.0, 1.0)):
    addStateAnnulus(x_1, name, color, offsetAnnulusRight)

def addStateAnnulus(x_1, name, color=(1.0, 1.0, 1.0, 1.0), offset = offsetAnnulusLeft):

    theta = x_1*(2*pi)
    rot = Matrix.Rotation(theta, 3, [0,0,1])
    pos = (rot @ Vector([major_radius, 0, 0])) + offset
    addSphere(pos, name, color)

# def addCamera(location, focus=cameraFocusPoint):
#     cam = bpy.data.cameras.new("Camera")
#     cam_ob = bpy.data.objects.new("Camera", cam)
#     bpy.context.collection.objects.link(cam_ob)
#     cam_ob.location = location
#     bpy.context.scene.camera = cam_ob
#     bpy.context.view_layer.objects.active = cam_ob
#     distance = getVectorNorm(location - focus)
#     update_camera(cam_ob, focus_point=focus, distance=distance)
#     return cam

#V is the major circle coordinate, U is the minor circle

def torusRestriction_mesh(torusLocation, 
    fromU=0.55/float(2*np.pi), toU=0.86/float(2*np.pi), fromV=0.0, toV=2*np.pi,
    offset = 0):

    U = np.arange(float(fromU), float(toU), 0.01)
    V = np.arange(float(fromV), float(toV), 0.01)
    ctr = 0
    verts = []
    faces = []
    for u in U:
      M = len(verts)
      for v in V:
        x = torusCoordinatesToGlobalCoordinates(u, v, offset)
        x = Vector((x[0]+torusLocation[0],x[1]+torusLocation[1],x[2]+torusLocation[2]))
        verts.extend([x])

      N = len(V)
      if ctr < len(U) - 1:
          for k in range(M,M + N - 1):
            faces.append( [k,k+1,k+N])
            faces.append( [k+1,k+1+N, k+N])

      ctr = ctr + 1

    mesh = bpy.data.meshes.new("trestrict")
    mesh.from_pydata(verts, [], faces)

    for p in mesh.polygons:
        p.use_smooth=True

    return mesh

def torusCoordinatesToGlobalCoordinates(u, v, offset = 0):
    r0 = torusMajorRadius
    r1 = torusMinorRadius + offset
    x = ((r0 + r1*cos(v))*cos(u), \
         (r0 + r1*cos(v))*sin(u), \
         r1*sin(v))
    return x

def addStateTorus(u, v, location = torusLocation, color=(1.0,1.0,1.0,1.0), size=diameterState, offset = 0):
    x = torusCoordinatesToGlobalCoordinates(u, v, offset)
    pos = Vector((x[0]+location[0],x[1]+location[1],x[2]+location[2]))
    addSphere(pos, "x_on_torus", color, size)

def addEdgeTorus(e, location=torusLocation, color=(1.0,1.0,1.0,1.0), width=diameterState,
    material=materialGreen, offset =0):
    curve = bpy.data.curves.new(name="EDGE_TORUS", type='CURVE')
    curve.dimensions = '3D'
    path_obj = bpy.data.objects.new("path_torus_annulus"+str(e[0,0]), curve)
    path_obj.location = (0,0,0)

    ### create milestones
    poly = curve.splines.new('POLY')

    poly.points.add(e.shape[0]-1)
    ctr = 0
    if e.shape[1]>1:
      for (u,v) in e:
        x = torusCoordinatesToGlobalCoordinates(u, v, offset)
        pt = Vector((x[0]+location[0],x[1]+location[1],x[2]+location[2]))
        poly.points[ctr].co = (pt[0],pt[1],pt[2],1)
        ctr = ctr + 1
    else:
      for (u) in e:
        x = torusCoordinatesToGlobalCoordinates(u, 0, offset)
        v = Vector((x[0]+location[0],x[1]+location[1],x[2]+location[2]))
        poly.points[ctr].co = (v[0],v[1],v[2],1)
        ctr = ctr + 1

    bpy.context.collection.objects.link(path_obj)

    curve.fill_mode = 'FULL'
    curve.bevel_depth = width

    path_obj.data.materials.append(material)


def addTorus(position, offset=-0.1):

    torus_mesh = bpy.ops.mesh.primitive_torus_add(major_radius = torusMajorRadius,
        minor_radius = torusMinorRadius + offset,
        major_segments = 64, minor_segments = 32, location=position)
    #64,32
    torus_obj = bpy.context.object
    torus_obj.name = 'Torus'
    torus_obj.data.materials.append(materialMagenta)
    # torus_obj.show_transparent = True #  displays trans in viewport

#def addComicOutlineObject(obj):
#  #obj = context.object
#  mat = bpy.data.materials["Material"]
#  obj.data.materials.append(mat)

#  mat.use_backface_culling = True

#  #remove surface
#  node_to_delete =  mat.node_tree.nodes['Principled BSDF']
#  mat.node_tree.nodes.remove( node_to_delete )

#  #add solidifer outline
#  solidifier = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
#  solidifier.thickness = -0.03
#  solidifier.use_flip_normals = True
#  solidifier.use_rim = False

#  ## TBD
#  solidifier.material_offset = 1
#  # solidifier.material_offset_rim = 1
#  # bpy.ops.object.mode_set(mode='EDIT')
#  # bpy.ops.mesh.edge_split()
#  # bpy.ops.mesh.separate(type='LOOSE')
#  # bpy.ops.object.mode_set()
#  # bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')


##https://blender.stackexchange.com/questions/157898/blender-2-8-python-how-do-i-find-my-material-output-node-and-assign-displacem

# materialConcrete = Material("/home/aorthey/git/blender/textures/darkconcrete.jpg")
# materialWood = Material("/home/aorthey/git/blender/textures/wood_texture.jpg")
# materialConcrete = bpy.data.materials.new(name="Texture")
# # materialTexture.diffuse_color = (1.0, 1.0, 1.0, 1.0)
# materialConcrete.metallic = 0.0
# materialConcrete.specular_intensity = 0.0
# materialConcrete.use_nodes = True
# bsdf = materialConcrete.node_tree.nodes["Principled BSDF"]
# texImage = materialConcrete.node_tree.nodes.new('ShaderNodeTexImage')
# texImage.image.filename = "/home/aorthey/git/blender/textures/concrete.jpeg"
# materialConcrete.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

# materialWood = Material("/home/aorthey/git/blender/textures/wood_texture.jpg")
# materialStainlessSteel = Material("/home/aorthey/git/blender/textures/stainless_steel.png")

def addBezierCurve(name, N =20, thickness=0.02):
  curve = bpy.data.curves.new(name="Trailblazer"+name, type='CURVE')
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
  curveObject.data.materials.append(materialRose)
  curveObject.show_transparent = True
  return curveObject

def setBackgroundColor(color):
  world = bpy.context.scene.world
  if world is None:
    new_world = bpy.data.worlds.new("New World")
    world = new_world
  world.use_nodes = True
  bg = world.node_tree.nodes['Background']
  bg.inputs[0].default_value = (color[0],color[1],color[2],1.0)
  bg.inputs[1].default_value = 1.0
  world.color = (color[0],color[1],color[2])

  # world = bpy.data.worlds["World"].node_tree.nodes['Background']

# def addTextureMaterial(obj, material):
#     if obj is None or obj.data is None:
#       return

#     # Assign it to object
#     if obj.data.materials:
#         obj.data.materials[0] = material
#     else:
#         obj.data.materials.append(material)

#     obj.active_material = material

#     bpy.ops.object.select_all(action='DESELECT')
#     obj.select_set(True)
#     bpy.ops.object.mode_set(mode='EDIT')
#     bpy.ops.mesh.select_all(action='SELECT')
#     bpy.ops.uv.smart_project()
#     bpy.ops.object.mode_set(mode='OBJECT')
#     bpy.ops.object.select_all(action='SELECT')

#     # obj.editmode_toggle()
#     # bpy.ops.uv.smart_project(angle_limit=66, island_margin = 0.02)
#     # obj.editmode_toggle()


import bpy
materialGreen = bpy.data.materials.new(name="Green")
materialGreen.diffuse_color = (0.0, 1.0, 0.0, 1.0)
materialGreen.metallic = 0.0
materialGreen.specular_intensity = 0.0

purplePosy = (236/256.0, 223/256.0, 237/256.0, 1.0)
rococoRose = (221/256.0, 146/256.0, 155/256.0, 1.0)
seasideSpray = (183/256.0, 204/256.0, 226/256.0, 1.0)

materialMagenta = bpy.data.materials.new(name="Magenta")
materialMagenta.diffuse_color = (0.205, 0.0, 0.37, 1.0)
materialMagenta.metallic = 0.9
materialMagenta.specular_intensity = 0.9

materialGrey = bpy.data.materials.new(name="NormalGrey")
materialGrey.diffuse_color = (0.2, 0.2, 0.2, 1.0)
materialGrey.metallic = 0.9
materialGrey.specular_intensity = 0.9

#######################################################
## material white: coloring for obstacles
#######################################################
materialWhite = bpy.data.materials.new(name="MWT")
materialWhite.diffuse_color = (0.9, 0.9, 0.9, 1.0)
materialWhite.metallic = 0.3
materialWhite.specular_intensity = 0.9

materialWhiteTransparent = bpy.data.materials.new(name="MWT")
materialWhiteTransparent.diffuse_color = materialWhite.diffuse_color
materialWhiteTransparent.metallic = materialWhite.metallic
materialWhiteTransparent.specular_intensity = materialWhite.specular_intensity

materialWhiteTransparent.use_nodes=True
nodes = materialWhiteTransparent.node_tree.nodes
for node in nodes:
    nodes.remove(node)
links = materialWhiteTransparent.node_tree.links

node_output  = nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = 400,0
node_pbsdf    = nodes.new(type='ShaderNodeBsdfPrincipled')
node_pbsdf.location = 0,0
materialWhiteTransparent.diffuse_color = (0.5, 0.5, 0.5, 1.0)
node_pbsdf.inputs['Base Color'].default_value = materialWhiteTransparent.diffuse_color
node_pbsdf.inputs['Alpha'].default_value = 0.5 # 1 is opaque, 0 is invisible
node_pbsdf.inputs['Roughness'].default_value = 0.2
node_pbsdf.inputs['Specular'].default_value = 0.9
node_pbsdf.inputs['Transmission'].default_value = 0.4 # 1 is fully transparent

link = links.new(node_pbsdf.outputs['BSDF'], node_output.inputs['Surface'])

materialWhiteTransparent.blend_method = 'HASHED'
materialWhiteTransparent.shadow_method = 'HASHED'
materialWhiteTransparent.use_screen_refraction = True

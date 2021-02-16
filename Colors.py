
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

class Colors():

  __init__(self, name):
    if name == "green":


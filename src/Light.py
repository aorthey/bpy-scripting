import bpy

def addLightSourceSun(location):
  name = "light_source_sun_"+str(location)
  light_data = bpy.data.lights.new(name=name, type='SUN')
  light_data.energy = 5
  light_data.angle = 5/180.0
  light_data.specular_factor = 0.8
  light_object = bpy.data.objects.new(name="light_2.80",
    object_data=light_data)
  bpy.context.collection.objects.link(light_object)
  light_object.location = location

def addLightSourcePoint(location, energy=6000):
  name = "light_source_point_"+str(location)
  light_data = bpy.data.lights.new(name=name, type='POINT')
  light_data.energy = energy
  light_data.specular_factor = 0.4
  light_data.use_contact_shadow = True
  light_object = bpy.data.objects.new(name="light_2.80",
    object_data=light_data)
  bpy.context.collection.objects.link(light_object)
  light_object.location = location

def addLightSourceArea(location, size=13, energy=400):
  name = "light_source_area_"+str(location)
  light_2 = bpy.data.lights.new(name=name, type='AREA')
  light_2.energy = energy
  light_2.size = size
  light_2_object = bpy.data.objects.new(name=name, object_data=light_2)
  bpy.context.collection.objects.link(light_2_object)
  light_2_object.location = location


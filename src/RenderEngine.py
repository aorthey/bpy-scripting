import bpy
import time
import sys, os 

# dirname = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(dirname)
from src.Utils import *
from src.Camera import *
from src.Light import *
from src.RaiLoader import *
from src.RaiAnim import *

class RenderEngine():

  def __init__(self, config):

    self.time_start_script = time.process_time()
    setBackgroundColor((.1,.1,.1))

    self.folder = config["folder"]
    self.Nsegments = config["Nsegments"]
    self.NkeyframeSteps = config["NkeyframeSteps"]
    self.renderImage = config["renderImage"]
    self.renderAnimation = config["renderAnimation"]
    self.cameraLocation = config["cameraLocation"]
    self.cameraFocusPoint = config["cameraFocusPoint"]
    self.dirname = config["dirname"]
    self.output_filename = config["output_filename"]
    self.obstacle_substring = config["obstacle_substring"]

    self.rai = RaiLoader(self.folder, self.obstacle_substring)
    self.rai.generateKeyframesFromAnim(self.Nsegments, self.NkeyframeSteps)

    lightLocation = 0.3*(self.cameraLocation-self.cameraFocusPoint)+Vector((0,0,+5))
    # addLightSourceSun(lightLocation, 2)
    addLightSourcePoint(lightLocation, 5000)

    ###############################################################################
    ## CAMERA SETUP
    ###############################################################################
    bpy.context.scene.frame_end += config["tPaddingEnd"]
    tend = bpy.context.scene.frame_end 
    camera = Camera(self.cameraLocation, self.cameraFocusPoint)

    if config["doZoom"]:
      tZoomStart = config["tZoomStart"]
      camera.zoomIn(tZoomStart, tZoomStart+50)
    if config["doZoomOut"]:
      tZoomOutDuration = config["tZoomOutDuration"]
      camera.zoomOut(tZoomStart+50+50, tZoomStart+50+50+tZoomOutDuration)

    tRotationStart = config["tRotationStart"]
    camera.rotate(tRotationStart, tend)

    ## set view to camera
    for area in bpy.context.screen.areas:
      if area.type == 'VIEW_3D':
        area.spaces[0].region_3d.view_perspective = 'CAMERA'
        break

    bpy.context.scene.eevee.use_ssr = True
    bpy.context.scene.eevee.use_ssr_refraction = True


  def Run(self):
    if not self.output_filename:
      self.output_filename = os.path.basename(os.path.dirname(self.folder))

    if self.renderImage:
      self.LastFrameToPNG(filename = self.dirname+"/output/"+self.output_filename+'.png')

    if self.renderAnimation:
      self.ToMP4(self.dirname+"/output/"+self.output_filename+".mp4")

    elapsed_time = time.process_time() - self.time_start_script
    print("TIME for RENDERING: %f (in s), %f (in m), %f (in h)"%\
        (elapsed_time,elapsed_time/60,elapsed_time/60/60))

#### IMAGE (PNG)
  def LastFrameToPNG(self, filename):
    bpy.context.scene.frame_set(bpy.context.scene.frame_end)
    renderEngine = bpy.context.scene.render
    # renderEngine.film_transparent = True
    renderEngine.image_settings.file_format = "PNG"
    renderEngine.image_settings.color_mode = 'RGBA'
    renderEngine.filepath = filename
    bpy.ops.render.render(write_still = True)
    ff = renderEngine.filepath
    os.system("convert -trim %s %s"%(ff,ff))
    print("Render Image [frame %d] to :%s"%(bpy.context.scene.frame_end,renderEngine.filepath))

  def ToMP4(self, filename):
    #### VIDEO (MP4)
    renderEngine = bpy.context.scene.render
    renderEngine.image_settings.file_format = "FFMPEG"
    renderEngine.ffmpeg.format = "MPEG4"
    renderEngine.ffmpeg.codec = "H264"
    renderEngine.ffmpeg.constant_rate_factor = "HIGH" #MEDIUM, LOW
    renderEngine.filepath = filename
    # renderEngine.film_transparent = True
    print("Starting to render %d frames."% bpy.context.scene.frame_end)
    bpy.ops.render.render(animation=True)


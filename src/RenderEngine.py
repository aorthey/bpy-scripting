import bpy
import os

class RenderEngine():
  def __init__(self, folder):

    bpy.context.scene.eevee.use_ssr = True
    bpy.context.scene.eevee.use_ssr_refraction = True


#### IMAGE (PNG)
  def LastFrameToPNG(self, filename):

    bpy.context.scene.frame_set(bpy.context.scene.frame_end)
    renderEngine = bpy.context.scene.render
    renderEngine.film_transparent = True
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
    print("Starting to render %d frames."% bpy.context.scene.frame_end)
    bpy.ops.render.render(animation=True)


import bpy
import bmesh
import numpy as np
import sys, os 
import re
import time
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

from src.RenderEngine import *

def renderPanda():
  configPanda = {
    "Nsegments": -1, #display N segments. -1: display all segments
    "NkeyframeSteps" : 1, #use every n-th keyframe, interpolate inbetween
    "folder": "data/anim_colored_v2/pandas/10/",
    "obstacle_substring": "cube",
    "cameraLocation": Vector((-3,-6,+2)),
    "cameraFocusPoint": Vector((0,0,0)),
    "dirname": dirname,
    "output_filename": "pandas_dark",
    "renderAnimation": True,
    "renderImage": True,
    "doZoom": False,
    "doZoomOut": False,
    "tPaddingEnd": 50,
    "tRotationStart": 50
  }
  renderPanda = RenderEngine(configPanda)
  renderPanda.Run()

def renderMobile():
  configMobile = {
    "Nsegments": -1, #display N segments. -1: display all segments
    "NkeyframeSteps" : 1, #use every n-th keyframe, interpolate inbetween
    "folder": "data/anim_colored_v2/mobile/10/",
    "obstacle_substring": "cube",
    "cameraLocation": Vector((-6,-12,+5)),
    "cameraFocusPoint": Vector((0,0,0)),
    "dirname": dirname,
    "output_filename": "mobile_manips_dark",
    "renderAnimation": True,
    "renderImage": True,
    "doZoom": False,
    "doZoomOut": False,
    "tPaddingEnd": 50,
    "tRotationStart": 50
  }
  renderMobile = RenderEngine(configMobile)
  renderMobile.Run()

def renderMobileTest():
  config = {
    "Nsegments": -1, #display N segments. -1: display all segments
    "NkeyframeSteps": 500, #use every n-th keyframe, interpolate inbetween
    "folder": "data/anim_colored_v2/mobile/10/",
    "obstacle_substring": "cube",
    "cameraLocation": Vector((-6,-12,+5)),
    "cameraFocusPoint": Vector((0,0,0)),
    "output_filename": "mobile_manips_test",
    "dirname": dirname,
    "renderAnimation": True,
    "renderImage": True,
    "doZoom": False,
    "doZoomOut": False,
    "tPaddingEnd": -200,
    "tRotationStart": 50
  }
  renderMobile = RenderEngine(config)
  renderMobile.Run()


# renderMobile()
renderPanda()
# renderMobileTest()

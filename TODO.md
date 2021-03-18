# TODO

* render one single endframe (without robots)
* Faster loading of keyframes by not using interpolation
for fcurve in obj.animation_data.action.fcurves:
  kf = fcurve.keyframe_points[-1]
  kf.interpolation = 'CONSTANT'

* Non-light emitting background
https://blenderartists.org/t/add-white-background-to-scene-without-lighting-scene/1206942
https://blenderartists.org/t/how-to-get-a-white-background-that-doesnt-emit-light/601130

* Smoother interpolation rot/zoom
* Better visualization of frame paths
* Visualize scheduler as guitar hero 


# Bpy-Scripting

![](https://raw.githubusercontent.com/aorthey/bpy-scripting/main/output/manipulator.png)
![](https://raw.githubusercontent.com/aorthey/bpy-scripting/main/output/well.png)
![](https://raw.githubusercontent.com/aorthey/bpy-scripting/main/output/2D_torus.png)

Set of scripts to generate photo-realistic animations in blender. Input to the
scripts are a collada file describing the scene and a text file Anim.txt which
describes how things move. Output can either be single image (at a specific
frame) or an animation.

# Features:

*  Scriptable camera (zoomIn(), zoomOut(), rotate())
*  Trailerblazer paths for specific frames ("gripper") to showcase motion
*  Easy color control for all objects (setColor(obj, colorRGB))

## Running the scripts:

You can either load the animation into the blender GUI (so that you can further
change things and then render), or you start the script in the background to
directly create images/animations.

### Run script and start GUI
```bash
./blender-2.83 --python rai.py
```

### Run script without starting GUI
```bash
./blender-2.83 --background --python rai.py
```

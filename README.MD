[> Blender NDS exporter:

Are you developping a 3D app for the Nintendo DS?
Are you using Blender to create astonishing 3D meshes?
This script allow you to export easily your Blender meshes into NDS binary "GL-like" CallLists.

[> Install:
Blender NDS Callist native OBJ + Texture exporter, supported on Windows 7/8/10 x86/x64:

Install these packages (deps/) IN ORDER, from the following directory:
- python-2-6-python-2.6-win32.msi
- blender-2.49b-windows.exe (do NOT run blender yet!)
- numpy-1.3.0-win32-superpack-python2.6.exe
- Pillow-2.7.0.win32-py2.6.exe

Copy the script "nds_3d_export.py" into the "scripts" directory of Blender:
C:\Users\[user profile]\AppData\Roaming\Blender Foundation\Blender\[user folder]\scripts

- Run Blender and check the File > Export menu : you'll find a new entry called "Nintendo DS CallList". 
  The ability to export NDS Callists using models + texture support should be available now.


[> Changelog:

v0.1:
    UV-textured meshes + Normals + Colors.
    Export into "C-style" format.
    Export Texture into PCX Format with correct size.
v0.2:
    Export into "Binary" format.
TODO :
    - 3D Animation support
    - Export directly into binary format

[> Infos :
author : Kevin Roy
website : blog.knokorpo.fr

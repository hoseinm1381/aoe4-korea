import bpy,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(R/'authoring/art014/hwacha/donor_geometry.blend'),load_ui=False,use_scripts=False)
recipe=runpy.run_path(str(R/'tools/art014/hwacha_recipe.py'))
recipe['start']()
bpy.ops.wm.save_as_mainfile(filepath='F:/aoe_4_temp/Temp_aoe4/hwacha-frame.blend')

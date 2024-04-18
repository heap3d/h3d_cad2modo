#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# re-initiate octane override
# ================================


import modo
import lx
from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import replace_file_ext


def reinitialize_octane_override(octane_override):
    # edit in schematic for each octane override material
    scene.deselect()
    lx.eval('!!select.subItem {} set'.format(octane_override.id))
    lx.eval('!!octane.materialMacro schematicEdit')


scene = modo.Scene()
log_name = replace_file_ext(scene.name)
h3dd = H3dDebug(enable=False, file=log_name)

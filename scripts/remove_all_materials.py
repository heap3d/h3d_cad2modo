#!/usr/bin/python
# ================================
# (C)2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# remove all advanced materials from scene, including not displaying one

import modo

from h3d_utilites.scripts.h3d_utils import replace_file_ext
from h3d_utilites.scripts.h3d_debug import H3dDebug

log_name = replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=False, file=log_name)


if __name__ == "__main__":
    items = modo.Scene().items(itype="advancedMaterial")
    for item in items:
        if item.parent:
            h3dd.print_debug(
                f"item name: <{item.name}>, type: <{item.type}>, parent type: <{item.parent.type}>"
            )
        else:
            h3dd.print_debug(
                f"item name: <{item.name}>, type: <{item.type}>, <No Parent>"
            )
        modo.Scene().removeItems(item, children=True)

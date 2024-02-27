#!/usr/bin/python
# ================================
# (C)2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# remove all advanced materials from scene, including not displaying one

import modo
import lx
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import replace_file_ext
from h3d_utilites.scripts.h3d_debug import H3dDebug


CMD_ADVANCED_MATERIALS = 'advanced_materials'


def remove_adv_materials():
    adv_materials = modo.Scene().items(itype=c.ADVANCEDMATERIAL_TYPE)
    for adv_material in adv_materials:
        modo.Scene().removeItems(adv_material, children=True)


def remove_masks():
    masks = modo.Scene().items(itype=c.MASK_TYPE)
    for mask in masks:
        modo.Scene().removeItems(mask, children=True)


def main():
    args = lx.args()
    if not args:
        remove_adv_materials()
        remove_masks()
        return

    if CMD_ADVANCED_MATERIALS in args:
        remove_adv_materials()
        return

    print(f"Unknow command(s): {' '.join(args)}")


log_name = replace_file_ext(modo.Scene().name)
h3dd = H3dDebug(enable=False, file=log_name)

if __name__ == "__main__":
    main()

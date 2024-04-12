#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# add material by polygon tag to selected mesh items

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import get_user_value
import h3d_cad2modo.scripts.h3d_kit_constants as h3dc
from h3d_cad2modo.scripts.unassigned_ptags import assign_materials_to_unassigned_ptags


def main():
    print('add_materials_by_tag_name_selected_mesh_specific.py start...')

    meshes = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    masks = modo.Scene().items(itype=c.MASK_TYPE)

    color = get_user_value(h3dc.USER_VAL_NAME_SPECIFIC_COLOR)
    assign_materials_to_unassigned_ptags(meshes, masks, use_color=True, color=color)

    lx.eval('select.type item')

    print('add_materials_by_tag_name_selected_mesh_specific.py done.')


if __name__ == '__main__':
    main()

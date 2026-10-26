#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# add material by polygon tag to selected mesh items

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import (
    get_user_value,
    execution_time_alarm,
    select_if_exists,
    set_selection_mode,
    SELECTION_MODE,
)

import h3d_cad2modo.scripts.h3d_kit_constants as h3dc
from h3d_cad2modo.scripts.unassigned_ptags import assign_materials_to_unassigned_ptags


@execution_time_alarm('Add Materials By Tag Name Selected Mesh Specific')
def main():
    meshes = scene.selectedByType(itype=c.MESH_TYPE)
    masks = scene.items(itype=c.MASK_TYPE)

    color = get_user_value(h3dc.USER_VAL_NAME_SPECIFIC_COLOR)
    assign_materials_to_unassigned_ptags(meshes, masks, use_color=True, color=color)

    set_selection_mode(SELECTION_MODE.ITEM.value)
    select_if_exists(meshes)


if __name__ == '__main__':
    scene = modo.Scene()
    main()

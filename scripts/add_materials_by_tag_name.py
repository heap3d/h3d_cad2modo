#!/usr/bin/python
# ================================
# (C)2022-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# add material by polygon tag to all mesh items

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import (
    execution_time_alarm,
    select_if_exists,
    set_selection_mode,
    SELECTION_MODE,
)

from h3d_cad2modo.scripts.unassigned_ptags import assign_materials_to_unassigned_ptags


@execution_time_alarm('Add Materials By Tag Name')
def main():
    meshes = scene.meshes
    masks = scene.items(itype=c.MASK_TYPE)
    assign_materials_to_unassigned_ptags(meshes, masks)

    set_selection_mode(SELECTION_MODE.ITEM.value)
    select_if_exists(meshes)


if __name__ == '__main__':
    scene = modo.Scene()
    main()

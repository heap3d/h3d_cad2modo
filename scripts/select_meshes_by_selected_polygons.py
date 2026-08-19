#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select mesh items who has polygons selected
# ================================

import modo
import lx

from scripts.select_meshes_by_selected_geo import get_item_by_selected_polygons

from h3d_utilites.scripts.h3d_utils import execution_time_alarm


@execution_time_alarm()
def main():
    meshes: list[modo.Mesh] = modo.Scene().items(itype='mesh')  # type: ignore

    selected_by_component = get_item_by_selected_polygons(meshes)

    lx.eval('select.type item')

    modo.Scene().deselect()
    for item in selected_by_component:
        item.select()


if __name__ == '__main__':
    main()

#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# fix holes with preselected polygons, 'undridge' style
# ================================

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import get_user_value, execution_time_alarm

from h3d_merge_tools.scripts.safe_merge import USERVAL_VMAP_NORMAL_PERFECT_NAME, DEFAULT_VMAP_NORMAL_PERFECT_NAME

from h3d_cad2modo.scripts.bridge_set_vertex_normals import is_vertex_normals_exist, set_vertex_normals


@execution_time_alarm('Fix holes unbridge')
def main():
    lx.eval('@AddBoundary.py')
    lx.eval('item.componentMode polygon true')
    lx.eval('delete')
    lx.eval('select.type edge')
    lx.eval('poly.make auto')
    lx.eval('select.type polygon')

    meshes = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    if not meshes:
        return

    vmap_name = get_user_value(USERVAL_VMAP_NORMAL_PERFECT_NAME)
    if not vmap_name:
        vmap_name = DEFAULT_VMAP_NORMAL_PERFECT_NAME

    for mesh in meshes:
        if is_vertex_normals_exist(mesh):
            set_vertex_normals(vmap_name)

    lx.eval('select.drop polygon')


if __name__ == "__main__":
    main()

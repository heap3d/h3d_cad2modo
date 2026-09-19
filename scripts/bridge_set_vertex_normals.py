#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# bridge selected, set vertex normals for newly created polygons

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import (
    drop_selection,
    select_polygons,
    SELECTION_MODE,
    set_selection_mode,
    get_selection_mode,
    get_user_value,
    )

from h3d_merge_tools.scripts.safe_merge import USERVAL_VMAP_NORMAL_PERFECT_NAME, DEFAULT_VMAP_NORMAL_PERFECT_NAME


def main():
    selected_meshes = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    if not selected_meshes:
        return

    mesh: modo.Mesh = selected_meshes[0]

    geometry = mesh.geometry
    if not mesh.geometry:
        print('No geometry in selected mesh')
        return
    polygons = geometry.polygons
    if not polygons:
        print('No polygons in selected mesh')

    polygons_before = set(polygons[:])   # type: ignore
    bridge_selected()
    polygons_after = set(polygons[:])  # type: ignore

    polygons_new = polygons_after.difference(polygons_before)

    old_selection_mode = get_selection_mode()
    set_selection_mode(SELECTION_MODE.POLYGON.value)
    drop_selection(SELECTION_MODE.POLYGON.value)
    select_polygons(polygons_new)

    vmap_name = get_user_value(USERVAL_VMAP_NORMAL_PERFECT_NAME)
    if not vmap_name:
        vmap_name = DEFAULT_VMAP_NORMAL_PERFECT_NAME
    set_vertex_normals(vmap_name)

    set_selection_mode(old_selection_mode)


def bridge_selected():
    lx.eval('tool.set BridgeBGCons on')
    lx.eval('tool.apply')
    lx.eval('tool.set BridgeBGCons off 0')


def set_vertex_normals(vmap_name: str = 'Vertex Normal'):
    lx.eval(f'vertMap.normals "{vmap_name}" true 1.0 "" false')


if __name__ == '__main__':
    main()

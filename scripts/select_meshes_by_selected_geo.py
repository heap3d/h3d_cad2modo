#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select mesh items who has geometry selected
# ================================

from typing import Iterable

import modo
import lx


def main():
    meshes: list[modo.Mesh] = modo.Scene().items(itype='mesh')  # type: ignore

    selected_by_vertices = get_item_by_selected_vertices(meshes)
    selected_by_edges = get_item_by_selected_edges(meshes)
    selected_by_polygons = get_item_by_selected_polygons(meshes)

    selected_by_geo = list(set(selected_by_vertices + selected_by_edges + selected_by_polygons))

    lx.eval('select.type item')

    modo.Scene().deselect()
    for item in selected_by_geo:
        item.select()


def get_item_by_selected_vertices(meshes: Iterable[modo.Mesh]) -> list[modo.Mesh]:
    selected_by_verts = [i for i in meshes if i.geometry.vertices.selected]  # type: ignore

    return selected_by_verts


def get_item_by_selected_edges(meshes: Iterable[modo.Mesh]) -> list[modo.Mesh]:
    selected_by_edges = [i for i in meshes if i.geometry.edges.selected]  # type: ignore

    return selected_by_edges


def get_item_by_selected_polygons(meshes: Iterable[modo.Mesh]) -> list[modo.Mesh]:
    selected_by_polys = [i for i in meshes if i.geometry.polygons.selected]  # type: ignore

    return selected_by_polys


if __name__ == '__main__':
    main()

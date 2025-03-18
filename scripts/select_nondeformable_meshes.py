#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select non-deformable meshes in the scene
# ================================

import modo

from h3d_cad2modo.scripts.select_deformable_meshes import get_meshes, get_nondeformable_from


def main():
    items = get_meshes(modo.Scene())
    meshes = get_nondeformable_from(items)

    if not meshes:
        return

    modo.Scene().deselect()
    for mesh in meshes:
        mesh.select()


if __name__ == '__main__':
    main()

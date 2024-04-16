#!/usr/bin/python
# ================================
# (C)2022-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# add material by polygon tag to all mesh items

import lx
import modo
import modo.constants as c

from h3d_cad2modo.scripts.unassigned_ptags import assign_materials_to_unassigned_ptags


def main():
    print('add_materials_by_tag_name.py start...')

    meshes = scene.meshes
    masks = scene.items(itype=c.MASK_TYPE)
    assign_materials_to_unassigned_ptags(meshes, masks)

    lx.eval('select.type item')

    print('add_materials_by_tag_name.py done.')


if __name__ == '__main__':
    scene = modo.Scene()
    main()

#!/usr/bin/python
# ================================
# (C)2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# set part tag for mesh items polygons to 'Default'

import modo
import modo.constants as c
import lx

from h3d_cad2modo.scripts.cad_materials_collect import set_polygon_part


def main():
    print('')
    print('clean_part_tags.py start...')

    meshes = modo.Scene().meshes
    if 'selected' in lx.args():
        meshes = modo.Scene().selectedByType(itype=c.MESH_TYPE)

    if not meshes:
        return

    for mesh in meshes:
        set_polygon_part(mesh)

    print('clean_part_tags.py done.')


if __name__ == '__main__':
    main()

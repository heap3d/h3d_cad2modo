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
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
from cad_materials_collect import set_polygon_part


def main():
    meshes = modo.Scene().meshes
    if lx.args:
        if lx.args[0] == '-selected':
            meshes = modo.Scene().selectedByType(itype=c.MESH_TYPE)

    if not meshes:
        return

    for mesh in meshes:
        set_polygon_part(mesh)


if __name__ == '__main__':
    main()

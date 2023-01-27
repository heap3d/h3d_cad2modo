#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# add material by polygon tag

import lx
import modo
import modo.constants as c
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
from unassigned_ptags import assign_materials_to_unassigned_ptags


def main():
    print('start...')

    meshes = modo.Scene().meshes
    masks = modo.Scene().items(itype=c.MASK_TYPE)
    assign_materials_to_unassigned_ptags(meshes, masks)

    print('done.')


if __name__ == '__main__':
    main()

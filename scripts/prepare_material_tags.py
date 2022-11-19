#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Adding color name prefix to the CAD color material tags

import modo
import lx
import modo.constants as c
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
from h3d_utils import H3dUtils
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
from h3d_kit_constants import *


def get_materials():
    return [i for i in modo.scene.current().items(itype=c.MASK_TYPE)
            if i.parent.type == h3du.type_int_to_str(c.POLYRENDER_TYPE)]


def rename_material(mask):
    if mask.name.startswith(COLOR_NAME_PREFIX):
        return
    if mask.channel('ptyp') is None:
        return
    if mask.channel('ptyp').get() != 'Material' and mask.channel('ptyp').get() != '':
        return
    if mask.channel('ptag').get() == '':
        return
    tag_name = mask.channel('ptag').get()
    lx.eval('poly.renameMaterial "{}" "{}"'.format(tag_name, '{}{}'.format(COLOR_NAME_PREFIX, tag_name)))


def main():
    print('start...')
    materials = get_materials()
    meshes = modo.scene.current().meshes
    for mesh in meshes:
        mesh.select()
    for mask in materials:
        rename_material(mask)
    print('done.')


h3du = H3dUtils()

if __name__ == '__main__':
    main()

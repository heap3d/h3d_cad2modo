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

from h3d_utilites.scripts.h3d_utils import itype_str

import h3d_cad2modo.scripts.h3d_kit_constants as h3dc


def get_materials(selected):
    if selected:
        return [i for i in scene.selectedByType(itype=c.MASK_TYPE)
                if i.parent.type == itype_str(c.POLYRENDER_TYPE)]
    else:
        return [i for i in scene.items(itype=c.MASK_TYPE)
                if i.parent.type == itype_str(c.POLYRENDER_TYPE)]  # type:ignore


def rename_material(mask):
    if mask.name.startswith(h3dc.COLOR_NAME_PREFIX):
        return
    if mask.channel('ptyp') is None:
        return
    if mask.channel('ptyp').get() != 'Material' and mask.channel('ptyp').get() != '':
        return
    if mask.channel('ptag').get() == '':
        return
    tag_name = mask.channel('ptag').get()
    lx.eval('poly.renameMaterial "{}" "{}"'.format(tag_name, '{}{}'.format(h3dc.COLOR_NAME_PREFIX, tag_name)))


def main():
    print('prepare_material_tags.py start...')

    SELECTED_MODE = 'selected' in lx.args()  # type:ignore

    materials = get_materials(SELECTED_MODE)

    meshes = scene.meshes
    for mesh in meshes:
        mesh.select()

    for mask in materials:
        rename_material(mask)

    print('prepare_material_tags.py done.')


if __name__ == '__main__':
    scene = modo.Scene()
    main()

#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# add material by polygon tag

from random import random
import lx
import modo
import modo.constants as c


def get_meshes():
    return modo.scene.current().items(itype=c.MESH_TYPE)


def add_materials_by_ptag(mesh):
    if not mesh:
        return
    mesh.select(replace=True)
    lx.eval('select.type polygon')
    ptags = set()
    for poly in mesh.geometry.polygons:
        if poly.materialTag not in ptags:
            poly.select(replace=True)
            rnd_color = '{} {} {}'.format(random(), random(), random())
            lx.eval('poly.setMaterial "{}" {{{}}} {} {} true false'.format(poly.materialTag, rnd_color, '0.8', '0.04'))
            ptags.add(poly.materialTag)


def main():
    print('start...')

    meshes = get_meshes()
    for mesh in meshes:
        add_materials_by_ptag(mesh)

    print('done.')


if __name__ == '__main__':
    main()

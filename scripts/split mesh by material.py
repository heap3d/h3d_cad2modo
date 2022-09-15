#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Split mesh by material

import modo
import modo.constants as c
import lx

scene = modo.scene.current()


def is_mask_valid(mask):
    # get scene render item
    render_item = scene.renderItem
    # return false if mask parent is not render item
    if mask.parent.id != render_item.id:
        return False
    channel = mask.channel('ptyp')
    # return false if no ptyp channel
    if channel is None:
        return False
    # return false if polygon type is not Material
    if mask.channel('ptyp').get() != 'Material':
        return False
    # return false if polygon tag set to (all)
    if mask.channel('ptag').get() == '':
        return False

    return True


def select_polys_selset_by_mask(mask):
    lx.eval('select.type polygon')
    try:
        lx.eval('!!select.useSet "{}" replace'.format(get_selset_name(mask.name)))
    except RuntimeError:
        return False

    return True


def remove_polys_selset_by_mask(mask):
    lx.eval('select.pickWorkingSet "{}" true'.format(get_selset_name(mask.name)))
    lx.eval('select.deleteWorkingSet')


def set_polys_selset_by_mask(mask):
    lx.eval('select.editSet "{}" add'.format(get_selset_name(mask.name)))


def get_selset_name(base_name):
    name = '$delete$ h3d split mesh by material - {}'.format(base_name)
    return name


def mesh_is_not_empty(mesh):
    if mesh is None:
        return False
    if mesh.type != 'mesh':
        return False
    if not len(mesh.geometry.polygons):
        return False
    return True


def main():
    print('')
    print('start...')

    material_masks = [mask for mask in scene.items(itype=c.MASK_TYPE) if is_mask_valid(mask)]
    initial_meshes = scene.meshes
    print('material masks count:<{}>'.format(len(material_masks)))
    print(initial_meshes)
    for mask in material_masks:
        # deselect all polygons
        lx.eval('select.type polygon')
        lx.eval('select.drop polygon')
        # deselect all items
        lx.eval('select.type item')
        scene.deselect()
        # select polygons by material
        mask.select()
        lx.eval('material.selectPolygons')
        set_polys_selset_by_mask(mask)
        for mesh in initial_meshes:
            print('<{}>:<{}>'.format(mask.name, mesh.name))
            lx.eval('select.type item')
            mesh.select(replace=True)
            if select_polys_selset_by_mask(mask):
                lx.eval('select.cut')
                if mesh_is_not_empty(mesh):
                    new_mesh = scene.addMesh(name=mesh.baseName)
                    new_mesh.select(replace=True)
                lx.eval('select.paste')
                remove_polys_selset_by_mask(mask)

    print('done.')


if __name__ == '__main__':
    main()

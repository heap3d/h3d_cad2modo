#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# save selected meshes as individual mesh assembly preset
# ================================

import modo
import modo.constants as c
import lx
import os.path

from h3d_utilites.scripts.h3d_utils import get_user_value

import h3d_cad2modo.scripts.h3d_kit_constants as h3dc


def save_solo_mesh_as_mesh_assembly_preset(mesh):
    print('solo mesh: <{}>'.format(mesh.name))
    # return if no mesh
    if mesh.type != 'mesh':
        print('wrong item.type: <{}>'.format(mesh.type))
        return
    # return if empty mesh
    if len(mesh.geometry.vertices) == 0:
        print('the mesh is empty')
        return
    scene.deselect()
    mesh.select()
    lx.eval('preset.createAssembly subtype:mesh')
    # get assembly group
    group_selected = scene.selectedByType(itype=c.GROUP_TYPE)
    print('assembly groups: <{}>'.format(group_selected))
    for group in group_selected:
        lx.eval('assembly.presetSave {} mesh "{}/{}.lxl" thumb:""'.format(group.id, REFLIB_DIR, mesh.name))


def save_multi_items_as_mesh_assembly_preset(item):
    print('multi items assembly parent: <{}>'.format(item.name))
    # return if no children
    if not item.children():
        return
    scene.deselect()
    item.select()
    # select all children
    for child in item.children(recursive=True):
        child.select()
    lx.eval('preset.createAssembly subtype:mesh')
    # get assembly group
    group_selected = scene.selectedByType(itype=c.GROUP_TYPE)
    for group in group_selected:
        lx.eval('assembly.presetSave {} mesh "{}/{}.lxl" thumb:""'.format(group.id, REFLIB_DIR, item.name))


def main():
    print('')
    print('octane_save_mesh_assembly_preset.py start...')
    # check if directory exist, ask for select one
    if not os.path.exists(REFLIB_DIR):
        modo.dialogs.alert(
            title='Directory error',
            message='Directory <{}> doesn\'t exist, please select valid reference library directory'.format(REFLIB_DIR),
            dtype='error'
        )
        return

    selected = scene.selected
    # get items with no parent
    root_items = [item for item in selected if not item.parent]
    print('root items list: {}'.format([i.name for i in root_items]))

    for item in root_items:
        if not item.children():
            save_solo_mesh_as_mesh_assembly_preset(item)
        else:
            save_multi_items_as_mesh_assembly_preset(item)

    print('octane_save_mesh_assembly_preset.py done.')


REFLIB_DIR = get_user_value(h3dc.USER_VAL_REFLIB_DIR_NAME)

if __name__ == '__main__':
    scene = modo.Scene()
    main()

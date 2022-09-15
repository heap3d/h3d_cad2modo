#!/usr/bin/python
# ================================
# (C)2019-2021 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# materials remap

import modo
import lx
import os.path

scene = modo.scene.current()
material_name_prefix = '#auto# '
auto_mask_list = set()
new_mask_list = set()
new_mask_ptag_list = set()
colors_map = {}
map_file_name = 'RGB Materials.txt'


def process_map_pair(str_line):
    str_stripped = str_line.strip()
    if str_stripped == '':
        return
    try:
        map_color_str, map_material_str = str_stripped.split('-')
    except ValueError:
        print('<{}> :: color - material split error'.format(str_stripped))
        return
    map_color_str = map_color_str.strip()
    map_material_str = map_material_str.strip()
    # remove multiple spaces in the strings
    map_color_str = ' '.join(map_color_str.split())
    map_material_str = ' '.join(map_material_str.split())
    if map_material_str == '':
        print('<{}> :: material string error'.format(str_stripped))
        return
    str_r, str_g, str_b = map_color_str.split()
    try:
        col_r = int(str_r)
        col_g = int(str_g)
        col_b = int(str_b)
        if col_r < 0 or col_r > 255:
            raise ValueError
        if col_g < 0 or col_g > 255:
            raise ValueError
        if col_b < 0 or col_b > 255:
            raise ValueError
    except ValueError:
        print('<{}> :: color string error'.format(str_stripped))
        return
    colors_map[map_color_str] = map_material_str
    return


def remap_color_by_material(str_color_to_replace, new_material_ptag):
    # remap color by material
    mask_remove_list = set()
    lx.eval('item.componentMode polygon true')  # enter polygon mode
    lx.eval('select.drop polygon')  # drop polygons
    lx.eval('item.componentMode polygon false')  # enter item mode
    scene.deselect()
    # set selection set by material
    for mask in scene.items(itype='mask'):
        if mask.channel('ptyp') is None:
            continue
        if mask.channel('ptyp').get() != 'Material':
            continue
        if not str(mask.name).startswith(material_name_prefix):
            continue
        if str_color_to_replace in mask.channel('ptag').get():
            mask.select()
            mask_remove_list.add(mask)
            lx.eval('material.selectPolygons')  # select polygons by material
            lx.eval('select.editSet "{}" add'.format(str_color_to_replace))  # create polygon selection set

    # assign material
    if len(mask_remove_list) < 1:
        return False
    scene.deselect()
    lx.eval('item.componentMode polygon false')  # enter item mode
    # select all meshes
    for item in scene.items(itype='mesh'):
        item.select()
    # enter polygon mode
    lx.eval('item.componentMode polygon true')  # enter polygon mode
    lx.eval('select.drop polygon')  # drop polygons
    # select selection set
    lx.eval('select.pickWorkingSet "{}" true'.format(str_color_to_replace))  # select selection
    # assign material
    lx.eval('poly.setMaterial "{}" {{{}}} 0.8 0.04 true false'.format(
        new_material_ptag,
        str_color_to_replace))  # assign material
    # remove color
    for mask in mask_remove_list:
        scene.removeItems(itm=mask, children=True)
    return True


print()
print('start...')

# get list of auto materials
for auto_mask in scene.items(itype='mask', name=material_name_prefix + '*'):
    auto_mask_list.add(auto_mask)

# get list of all materials except auto
for new_mask in scene.items(itype='mask'):
    if new_mask.name.startswith(material_name_prefix):
        continue
    if new_mask.channel('ptyp').get() != 'Material':
        continue
    if new_mask.channel('ptag').get() == '':
        continue
    new_mask_list.add(new_mask)
    new_mask_ptag_list.add(new_mask.channel('ptag').get())

# load materials pairs from file 'RGB Materials.txt'
# open the file
file_path = map_file_name
if not os.path.exists(file_path):
    file_path = os.path.dirname(scene.filename) + '/' + map_file_name
    if not os.path.exists(file_path):
        file_path = modo.dialogs.dirBrowse(title="Select material map file")
if not os.path.exists(file_path):
    print('can\'t find file: <{}>\nexit.'.format(map_file_name))
    exit()
map_file = open(file_path, 'r')

# load material pairs
for line in map_file:
    process_map_pair(line)

map_file.close()

for key in colors_map.keys():
    if colors_map[key] not in new_mask_ptag_list:
        print('<{}> :: <{}> - not found! Error in material tag : <{}>'.format(key, colors_map[key], colors_map[key]))
        continue
    if remap_color_by_material(key, colors_map[key]):
        print('<{}> :: <{}> - replaced'.format(key, colors_map[key]))

lx.eval('select.drop polygon')  # drop polygons
lx.eval('item.componentMode polygon false')  # enter item mode
scene.deselect()

print('done.')

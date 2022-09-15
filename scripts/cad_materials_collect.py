#!/usr/bin/python
# ================================
# (C)2019-2021 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# CAD materials collector

import modo
import modo.constants as c
import lx

scene = modo.scene.current()


def get_materials_from_masks(masks):
    materials = list()
    for mask in masks:
        for child in mask.children():
            if child.type == 'advancedMaterial':
                materials.append(child)
    return materials


def main():
    rgb_colors_str = {}  # set of unique colors
    material_name_prefix = '#color# '
    is_int_colors = False

    print('')
    print('start...')

    # collect unique colors into rgb_color_str set of ptag sets
    material_masks = scene.selectedByType(itype=c.MASK_TYPE)
    if not material_masks:
        material_masks = scene.items(itype=c.MASK_TYPE)
    materials = get_materials_from_masks(material_masks)
    for material in materials:
        color_red = material.channel('diffCol.R').get()  # read diffuse color values
        color_green = material.channel('diffCol.G').get()  # read diffuse color values
        color_blue = material.channel('diffCol.B').get()  # read diffuse color values
        if isinstance(color_red, int):
            is_int_colors = True  # check if values is in integer format
        elif isinstance(color_red, float):
            is_int_colors = False  # check if values is in float format
        else:
            print('Error color value type. Switch to <int> or <float>. Exit')
            exit()
        if is_int_colors:
            color_name = '{} {} {}'.format(
                str(color_red).zfill(3),
                str(color_green).zfill(3),
                str(color_blue).zfill(3)
            )  # write color string in integer format
        else:
            color_name = '{} {} {}'.format(
                str(int(color_red * 255 + 0.5)).zfill(3),
                str(int(color_green * 255 + 0.5)).zfill(3),
                str(int(color_blue * 255 + 0.5)).zfill(3)  # write color string float to integer converted
            )
        if material.parent is None:
            continue
        channel = material.parent.channel('ptyp')  # check if ptyp is not None
        if channel is None:
            continue
        if material.parent.channel('ptyp').get() != 'Material':  # check if ptyp is set to Material
            continue
        ptag = material.parent.channel('ptag').get()  # get ptag
        if ptag == '':
            continue
        if not (color_name in rgb_colors_str):
            rgb_colors_str[color_name] = set()  # set of ptag's for specific color
        rgb_colors_str[color_name].add(ptag)

    # convert ptag sets into polygon selection sets
    for color_str in rgb_colors_str:
        scene.deselect()
        # lx.eval('item.componentMode polygon true')  # enter polygon mode
        lx.eval('select.drop polygon')  # drop polygon selection
        for ptag in rgb_colors_str[color_str]:
            ptag_loop_counter = 0
            for mask in scene.items(itype='mask'):
                if mask.channel('ptyp') is None:
                    continue
                if mask.channel('ptyp').get() != 'Material':
                    continue
                if str(mask.name).startswith(material_name_prefix):
                    continue
                if mask.channel('ptag').get() == ptag:
                    mask.select()
        lx.eval('material.selectPolygons')  # select poly by material
        lx.eval('select.editSet "{}" add'.format(color_str))  # create polygon selection set

    scene.deselect()
    lx.eval('item.componentMode polygon false')  # enter item mode
    # select all meshes
    for item in scene.items('mesh'):
        item.select()
    # enter polygon mode
    lx.eval('item.componentMode polygon true')  # enter polygon mode
    # assign new material for valid colors
    for color_str in rgb_colors_str:
        # select selection set
        print('color_str: <{}>'.format(color_str))
        lx.eval('select.pickWorkingSet "{}" true'.format(color_str))  # select polygon selection set
        # assign material
        str_r, str_g, str_b = color_str.split()
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
            print('<{}> :: color string error'.format(color_str))
            continue
        if is_int_colors:
            lx.eval('poly.setMaterial "{}" {{{} {} {}}} 0.8 0.04 true false'.format(
                material_name_prefix+color_str,
                col_r,
                col_g,
                col_b)
            )  # assign material with INTEGER values
        else:
            lx.eval('poly.setMaterial "{}" {{{} {} {}}} 0.8 0.04 true false'.format(
                material_name_prefix+color_str,
                col_r/255.0,
                col_g/255.0,
                col_b/255.0)
            )  # assign material with FLOAT values

    # create list of material mask items to remove
    remove_list = set()
    # fill remove_list
    for mask in scene.items(itype='mask'):
        mask.select(replace=True)
        # get the mesh item for the shader group 'mask.setMesh ?', skip if none
        if lx.eval('mask.setMesh ?') == '(all)':
            continue
        # disconnect mask from group locator
        lx.eval('mask.setMesh (all)')
        remove_list.add(mask)
    # remove material mask items in the list
    for item in remove_list:
        scene.removeItems(itm=item, children=True)

    # remove processed material masks
    for mask in material_masks:
        scene.removeItems(mask, children=True)

    lx.eval('select.type item')
    print('done.')


if __name__ == '__main__':
    main()

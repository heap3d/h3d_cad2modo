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


def get_materials_from_masks(masks):
    materials = list()
    for mask in masks:
        for child in mask.children():
            if child.type == 'advancedMaterial':
                materials.append(child)
    return materials


def main():
    # set of unique colors
    rgb_colors_str = {}
    material_name_prefix = '#color# '
    is_int_colors = False

    print('')
    print('start...')

    # collect unique colors into rgb_color_str set of ptag sets
    material_masks = modo.scene.current().selectedByType(itype=c.MASK_TYPE)
    if not material_masks:
        material_masks = modo.scene.current().items(itype=c.MASK_TYPE)
    materials = get_materials_from_masks(material_masks)
    for material in materials:
        # read diffuse color values
        color_red = material.channel('diffCol.R').get()
        # read diffuse color values
        color_green = material.channel('diffCol.G').get()
        # read diffuse color values
        color_blue = material.channel('diffCol.B').get()
        if isinstance(color_red, int):
            # check if values is in integer format
            is_int_colors = True
        elif isinstance(color_red, float):
            # check if values is in float format
            is_int_colors = False
        else:
            print('Error color value type. Switch to <int> or <float>. Exit')
            exit()
        if is_int_colors:
            # write color string in integer format
            color_name = '{} {} {}'.format(
                str(color_red).zfill(3),
                str(color_green).zfill(3),
                str(color_blue).zfill(3)
            )
        else:
            color_name = '{} {} {}'.format(
                str(int(color_red * 255 + 0.5)).zfill(3),
                str(int(color_green * 255 + 0.5)).zfill(3),
                # write color string float to integer converted
                str(int(color_blue * 255 + 0.5)).zfill(3)
            )
        if material.parent is None:
            continue
        # check if ptyp is not None
        channel = material.parent.channel('ptyp')
        if channel is None:
            continue
        # check if ptyp is set to Material
        if material.parent.channel('ptyp').get() != 'Material':
            continue
        # get ptag
        ptag = material.parent.channel('ptag').get()
        if ptag == '':
            continue
        if not (color_name in rgb_colors_str):
            # set of ptag's for specific color
            rgb_colors_str[color_name] = set()
        rgb_colors_str[color_name].add(ptag)

    # convert ptag sets into polygon selection sets
    for color_str in rgb_colors_str:
        modo.scene.current().deselect()
        # drop polygon selection
        lx.eval('select.drop polygon')
        for ptag in rgb_colors_str[color_str]:
            for mask in modo.scene.current().items(itype='mask'):
                if mask.channel('ptyp') is None:
                    continue
                if mask.channel('ptyp').get() != 'Material':
                    continue
                if str(mask.name).startswith(material_name_prefix):
                    continue
                if mask.channel('ptag').get() == ptag:
                    mask.select()
        # select poly by material
        lx.eval('material.selectPolygons')
        # create polygon selection set
        lx.eval('select.editSet "{}" add'.format(color_str))

    modo.scene.current().deselect()
    # enter item mode
    lx.eval('item.componentMode polygon false')
    # select all meshes
    for item in modo.scene.current().items(itype=c.MESH_TYPE):
        item.select()
    # enter polygon mode
    lx.eval('item.componentMode polygon true')
    # assign new material for valid colors
    for color_str in rgb_colors_str:
        # select polygon selection set
        lx.eval('select.pickWorkingSet "{}" true'.format(color_str))
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
            # assign material with INTEGER values
            lx.eval('poly.setMaterial "{}" {{{} {} {}}} 0.8 0.04 true false'.format(
                material_name_prefix+color_str,
                col_r,
                col_g,
                col_b)
            )
        else:
            # assign material with FLOAT values
            lx.eval('poly.setMaterial "{}" {{{} {} {}}} 0.8 0.04 true false'.format(
                material_name_prefix+color_str,
                col_r/255.0,
                col_g/255.0,
                col_b/255.0)
            )

    # create list of material mask items to remove
    remove_list = set()
    # fill remove_list
    for mask in modo.scene.current().items(itype=c.MASK_TYPE):
        mask.select(replace=True)
        # get the mesh item for the shader group 'mask.setMesh ?', skip if none
        if lx.eval('mask.setMesh ?') == '(all)':
            continue
        # disconnect mask from group locator
        lx.eval('mask.setMesh (all)')
        remove_list.add(mask)
    # remove material mask items in the list
    for item in remove_list:
        modo.scene.current().removeItems(itm=item, children=True)

    # remove processed material masks
    for mask in material_masks:
        modo.scene.current().removeItems(mask, children=True)

    lx.eval('select.type item')
    print('done.')


if __name__ == '__main__':
    main()

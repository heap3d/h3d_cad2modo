#!/usr/bin/python
# ================================
# (C)2019-2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# consolidate CAD materials based on equal colors

from enum import Enum
import modo
import modo.constants as c
import lx
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
import h3d_utils as h3du
from h3d_debug import H3dDebug
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
import h3d_kit_constants as h3dc


class ColorMode(Enum):
    undefined = 0
    color_int = 1
    color_float = 2


def detect_color_mode():
    materials = modo.Scene().items(itype=c.ADVANCEDMATERIAL_TYPE)
    if not materials:
        return ColorMode.undefined

    material = materials[0]
    color_red = material.channel('diffCol.R').get()

    if isinstance(color_red, int):
        # check if values is in integer format
        return ColorMode.color_int

    elif isinstance(color_red, float):
        # check if values is in float format
        return ColorMode.color_int

    else:
        print('Error color value type. Switch to <int> or <float>. Exit')
        raise ValueError('Error color value type. Switch to <int> or <float>. Exit')


def get_color_mode():
    global color_mode

    if not color_mode:
        color_mode = detect_color_mode()

    return color_mode


def get_materials_from_masks(masks):
    h3dd.indent_inc()
    h3dd.print_items(masks, 'get_materials_from_mask() enter: masks:')
    materials = list()
    for mask in masks:
        h3dd.print_debug('mask: <{}>'.format(mask.name))
        for child in mask.children():
            h3dd.print_debug('child: <{}>'.format(child.name), 1)
            if child.type == h3du.itype_str(c.ADVANCEDMATERIAL_TYPE):
                materials.append(child)
                h3dd.print_debug('child added', 2)

    h3dd.print_items(materials, 'materials collected:')
    h3dd.print_debug('get_materials_from_mask() exit')
    h3dd.indent_dec()
    return materials


def color_num_to_str(color_red, color_green, color_blue):
    color_int_str = ''

    if get_color_mode() == ColorMode.color_int:
        # write color string in integer format
        color_int_str = '{} {} {}'.format(
            str(color_red).zfill(3),
            str(color_green).zfill(3),
            str(color_blue).zfill(3)
        )
    else:
        # write color string float to integer converted
        color_int_str = '{} {} {}'.format(
            str(int(color_red * 255 + 0.5)).zfill(3),
            str(int(color_green * 255 + 0.5)).zfill(3),
            str(int(color_blue * 255 + 0.5)).zfill(3)
        )

    return color_int_str


def collect_unique_colors(materials):
    # set of unique colors
    rgb_colors_str = {}

    for material in materials:
        # read diffuse color values
        color_red = material.channel('diffCol.R').get()
        color_green = material.channel('diffCol.G').get()
        color_blue = material.channel('diffCol.B').get()

        color_name = color_num_to_str(color_red, color_green, color_blue)

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

    return rgb_colors_str


def ptag_to_selection_set(rgb_colors_str):
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

                if str(mask.name).startswith(h3dc.COLOR_NAME_PREFIX):
                    continue

                if mask.channel('ptag').get() == ptag:
                    mask.select()

        # select poly by material
        lx.eval('material.selectPolygons')
        # create polygon selection set
        lx.eval('select.editSet "{}" add'.format(color_str))


def assign_materials(rgb_colors_str):
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

        if get_color_mode() == ColorMode.color_int:
            # assign material with INTEGER values
            lx.eval('poly.setMaterial "{}" {{{} {} {}}} 0.8 0.04 true false'.format(
                h3dc.COLOR_NAME_PREFIX+color_str,
                col_r,
                col_g,
                col_b)
            )
        else:
            # assign material with FLOAT values
            lx.eval('poly.setMaterial "{}" {{{} {} {}}} 0.8 0.04 true false'.format(
                h3dc.COLOR_NAME_PREFIX+color_str,
                col_r/255.0,
                col_g/255.0,
                col_b/255.0)
            )


def get_masks_with_item_tag(masks):
    # create list of material mask items to remove
    remove_list = set()

    # fill remove_list
    for mask in masks:
        mask.select(replace=True)

        # get the mesh item for the shader group 'mask.setMesh ?', skip if none
        if lx.eval('mask.setMesh ?') == '(all)':
            continue

        # disconnect mask from group locator
        lx.eval('mask.setMesh (all)')
        remove_list.add(mask)

    return remove_list


def get_scene_masks():
    return modo.scene.current().items(itype=c.MASK_TYPE)


def get_selected_masks():
    return modo.scene.current().selectedByType(itype=c.MASK_TYPE)


def is_simple_mask(mask):
    if len(mask.children(recursive=True)) != 1:
        return False
    if mask.children()[0].type != h3du.itype_str(c.ADVANCEDMATERIAL_TYPE):
        return False

    return True


def is_similar_colors(mask1, mask2):
    pass


def has_color_prefix(mask):
    pass


def main():
    print('')
    print('start...')

    SELECTED_MODE = 'selected' in lx.args()

    # get material masks
    if SELECTED_MODE:
        material_masks = get_selected_masks()
        h3dd.print_items(material_masks, 'material_masks selected:')
    else:
        material_masks = get_scene_masks()
        h3dd.print_items(material_masks, 'material_masks scene:')

    # [ ] TODO add color pefix to unique simple masks

    # [ ] TODO get list of duplicated simple masks

    # get materials from material_masks
    materials = get_materials_from_masks(material_masks)
    h3dd.print_items(materials, 'materials:')

    # collect unique colors into rgb_color_str set of ptag sets
    rgb_colors_str = collect_unique_colors(materials)
    h3dd.print_items(rgb_colors_str, 'rgb_colors_str:')

    # convert ptag sets into polygon selection sets
    ptag_to_selection_set(rgb_colors_str)

    modo.scene.current().deselect()
    # enter item mode
    lx.eval('item.componentMode polygon false')
    # select all meshes
    for item in modo.scene.current().items(itype=c.MESH_TYPE):
        item.select()

    # enter polygon mode
    lx.eval('item.componentMode polygon true')
    # assign new material for valid colors
    assign_materials(rgb_colors_str)

    # create list of material mask items to remove
    item_masks = get_masks_with_item_tag(modo.scene.current().items(itype=c.MASK_TYPE))
    # [ ] TODO get remove_list from item_masks
    h3dd.print_items(remove_list, 'remove_list:')
    # remove material mask items in the list
    h3dd.print_debug('remove_list items deletion...')
    for item in remove_list:
        # modo.scene.current().removeItems(itm=item, children=True)
        h3du.remove_if_exist(item, children=True)
    h3dd.print_debug('remove_list items deleted')

    # remove processed material masks
    h3dd.print_debug('material_masks items deletion...')
    for mask in material_masks:
        h3dd.print_debug('removing <{}>...'.format(mask.name))
        result = h3du.remove_if_exist(mask, children=True)
        h3dd.print_debug('result: {}'.format(result), 1)
    h3dd.print_debug('material_masks items deleted')

    lx.eval('select.type item')

    print('done.')


log_name = h3du.replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=False, file=log_name)

color_mode = ColorMode.undefined

if __name__ == '__main__':
    main()

#!/usr/bin/python
# ================================
# (C)2019-2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# consolidate CAD materials based on equal colors

import modo
import modo.constants as c
import lx
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
import h3d_utils as h3du
from h3d_debug import H3dDebug
from h3d_exceptions import H3dExitException
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
import h3d_kit_constants as h3dc
from prepare_material_tags import rename_material
from ptag_to_selection_set import ptag_to_selection_set


def get_materials_from_masks(masks):
    materials = []
    for mask in masks:
        for child in mask.children():
            if child.type == h3du.itype_str(c.ADVANCEDMATERIAL_TYPE):
                materials.append(child)

    return materials


def color_num_to_str(color_red, color_green, color_blue):
    color_int_str = ''
    # write color string float to integer converted
    color_int_str = '{} {} {}'.format(
        str(int(color_red * 255 + 0.5)).zfill(3),
        str(int(color_green * 255 + 0.5)).zfill(3),
        str(int(color_blue * 255 + 0.5)).zfill(3)
    )

    return color_int_str


def collect_unique_ptags_by_color(materials):
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


def assign_materials(rgb_colors_str):
    # select all meshes
    meshes = modo.Scene().items(itype=c.MESH_TYPE)
    modo.Scene().deselect()
    for mesh in meshes:
        mesh.select()

    # enter polygon mode
    lx.eval('select.type polygon')

    # assign new material for valid colors
    for color_str in rgb_colors_str:
        # select polygon selection set
        h3dd.print_debug('assign_materials: <{}>'.format(color_str))
        lx.eval('select.pickWorkingSet "{}" true'.format(color_str))

        # assign material
        str_r, str_g, str_b = color_str.split()

        try:
            col_r = int(str_r)
            col_g = int(str_g)
            col_b = int(str_b)

            if col_r < 0 or col_r > 255:
                raise ValueError('RGB R value out of 0..255 range')

            if col_g < 0 or col_g > 255:
                raise ValueError('RGB G value out of 0..255 range')

            if col_b < 0 or col_b > 255:
                raise ValueError('RGB B value out of 0..255 range')

        except ValueError:
            print('<{}> :: color string error'.format(color_str))
            continue

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


def has_color_prefix(mask, prefix):
    if not mask:
        return None
    if not prefix:
        return None
    return mask.name.startswith(prefix)


def get_siblings(mask):
    if not mask:
        return None
    if mask.parent is None:
        return []
    if mask.parent.type == h3du.itype_str(c.POLYRENDER_TYPE):
        return []

    return [item for item in mask.parent.childrenByType(itype=c.MASK_TYPE) if item != mask]


def get_duplicated_color_masks(masks):
    duplicated_masks = set()
    color_strings = dict()

    for mask in masks:
        material = mask.children()[0]
        # read diffuse color values
        color_red = material.channel('diffCol.R').get()
        color_green = material.channel('diffCol.G').get()
        color_blue = material.channel('diffCol.B').get()

        color_str = color_num_to_str(color_red, color_green, color_blue)

        if color_str not in color_strings:
            color_strings[color_str] = 0
        color_strings[color_str] += 1
        if color_strings[color_str] > 1:
            duplicated_masks.add(mask)

    return duplicated_masks


def is_protected(mask):
    # [ ] TODO check if protected
    return False


def main():
    print('')
    print('start...')

    initial_masks = get_scene_masks()

    # get simple_masks
    simple_masks = set([mask for mask in initial_masks
                        if is_simple_mask(mask) and not has_color_prefix(mask, h3dc.COLOR_NAME_PREFIX)])

    # get validated_simple_masks
    validated_simple_masks = set()
    for mask in simple_masks:
        siblings = get_siblings(mask)
        if any(not is_simple_mask(item) for item in siblings):
            continue
        parents = mask.parents
        parents_masks = [item for item in parents if item.type == h3du.itype_str(c.MASK_TYPE)]
        if any(item.channel('ptyp').get() == 'Material' for item in parents_masks):
            continue
        validated_simple_masks.add(mask)

    # get duplicated_simple_masks
    # duplicated_simple_masks = get_duplicated_color_masks(validated_simple_masks)

    # get unique_simple_masks
    # unique_simple_masks = validated_simple_masks - duplicated_simple_masks
    # # add color pefix to unique simple masks
    # for mask in unique_simple_masks:
    #     rename_material(mask)

    # materials = get_materials_from_masks(duplicated_simple_masks)
    # rgb_color_strings = collect_unique_ptags_by_color(materials)
    # ptag_to_selection_set(rgb_color_strings, h3dc.COLOR_NAME_PREFIX)

    # h3dd.exit('debug exit: ptag to selection sets')

    # ---------- process duplicated materials ----------

    # get materials from material_masks
    h3dd.print_items(validated_simple_masks, 'validated_simple_masks <{}>:'.format(len(validated_simple_masks)))
    materials = get_materials_from_masks(validated_simple_masks)
    h3dd.print_items(materials, 'materials <{}>:'.format(len(materials)))

    # collect unique colors into rgb_color_str set of ptag sets
    rgb_color_strings = collect_unique_ptags_by_color(materials)
    h3dd.print_items(rgb_color_strings, 'rgb_color_strings <{}>:'.format(len(rgb_color_strings)))

    modo.scene.current().deselect()
    # enter item mode
    lx.eval('select.type item')
    # select all meshes
    for item in modo.scene.current().items(itype=c.MESH_TYPE):
        item.select()

    # convert ptag sets into polygon selection sets
    ptag_to_selection_set(rgb_color_strings, h3dc.COLOR_NAME_PREFIX)

    # assign new material for valid colors
    assign_materials(rgb_color_strings)

    # create list of material mask items to remove
    remove_list = set()
    remove_list.update(validated_simple_masks)
    h3dd.print_items(remove_list, 'remove_list:')
    # h3dd.exit('debug exit: materials assigned. before deleting item masks')
    item_masks = get_masks_with_item_tag(modo.scene.current().items(itype=c.MASK_TYPE))
    h3dd.print_items(item_masks, 'item_masks:')
    # add item masks to remove_list if no used materials in there
    for item_mask in item_masks:
        if is_protected(item_mask):
            continue
        remove_list.add(item_mask)

    # remove material mask items in the list
    h3dd.print_items(remove_list, 'remove_list:')
    for item in remove_list:
        # modo.scene.current().removeItems(itm=item, children=True)
        h3du.remove_if_exist(item, children=True)

    lx.eval('select.type item')

    print('done.')


log_name = h3du.replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=True, file=log_name)

color_mode = None

if __name__ == '__main__':
    try:
        main()
    except H3dExitException as e:
        print(e.message)

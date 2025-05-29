#!/usr/bin/python
# ================================
# (C)2021-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# materials remap modo UI (color material map)

import os.path
import sys
import lx
import modo
import modo.constants as c

import h3d_cad2modo.scripts.h3d_kit_constants as h3dc

from h3d_utilites.scripts.h3d_utils import (
    get_user_value,
    set_user_value,
    is_material_ptyp,
    replace_file_ext,
    is_defined_user_value,
    def_new_user_value,
    delete_defined_user_value,
)
from h3d_utilites.scripts.h3d_debug import H3dDebug

UV_TYPE_STRING = 'string'
UV_TYPE_INTEGER = 'integer'
UV_TYPE_COLOR = 'color'
UV_LIFE_TEMPORARY = 'temporary'

CMD_PREV = '-prev'
CMD_NEXT = '-next'
CMD_SCAN = '-scan'
CMD_SAVE = '-save'
CMD_LOAD = '-load'
CMD_APPLY = '-apply'
CMD_SELECT = '-select'
CMD_CREATE_MISSING_MATS = '-createmats'

DEFAULT = 'default'


def get_page_start():
    page_start = get_user_value(h3dc.USERVAL_NAME_PAGE_START)
    return page_start


def set_page_start(start, tags):
    if start >= len(tags):
        start = len(tags) - 1
    if start < 1:
        start = 1
    set_user_value(h3dc.USERVAL_NAME_PAGE_START, start)
    return get_page_start()


def get_command(args: list[str]):
    cmd_map = {
        CMD_PREV: CMD_PREV,
        CMD_NEXT: CMD_NEXT,
        CMD_SCAN: CMD_SCAN,
        CMD_SAVE: CMD_SAVE,
        CMD_LOAD: CMD_LOAD,
        CMD_APPLY: CMD_APPLY,
        CMD_SELECT: CMD_SELECT,
        CMD_CREATE_MISSING_MATS: CMD_CREATE_MISSING_MATS,
    }
    return cmd_map.get(args[0], CMD_SCAN)


def get_tags_list(command):
    tags = list()
    if command != CMD_SCAN:
        # read colors list from user value
        try:
            colors_string_store = get_user_value(h3dc.USERVAL_NAME_COLORS_STORE)
            tags.extend(colors_string_store.split(';'))
        except RuntimeError:
            print('The scene is not scanned. Press the <scan scene> button to scan.')
            sys.exit()

        h3dd.print_items(tags, 'tags fron user value:')
        return tags

    # get material tag from mesh polygons
    for mesh in scene.items(itype=c.MESH_TYPE):
        for polygon in mesh.geometry.polygons:
            try:
                tag = polygon.materialTag
            except LookupError:
                tag = None
            if tag is None:
                continue
            if tag == '':
                continue
            if tag not in tags:
                # add tag to tags list
                tags.append(tag)
    # sort tags list
    tags.sort()
    # insert dummy line at the start for indexing consistency
    tags.insert(0, h3dc.DEFAULT_MATERIAL_ASSIGNMENT)
    # store colors list in user value
    colors_string_store = ';'.join(tags)
    # create user value if not created
    if not is_defined_user_value(h3dc.USERVAL_NAME_COLORS_STORE):
        def_new_user_value(
            h3dc.USERVAL_NAME_COLORS_STORE, UV_TYPE_STRING, UV_LIFE_TEMPORARY
        )
    # store colors string
    set_user_value(h3dc.USERVAL_NAME_COLORS_STORE, colors_string_store)

    if len(tags) < 1 or (len(tags) == 1 and tags[0] == ''):
        print(
            'Void tags list. Try to scan scene or run Consolidate CAD Materials script first.'
        )
        sys.exit()

    h3dd.print_items(tags, 'tags from geometry:')
    return tags


def get_materials_list(command, tags):
    if command != CMD_SCAN:
        materials_string_store = get_user_value(h3dc.USERVAL_NAME_MATERIALS_STORE)

        h3dd.print_items(
            list(materials_string_store.split('\t')), 'materials from user value:'
        )
        return list(materials_string_store.split('\t'))

    materials_set = set()
    h3dd.print_items(scene.items(itype='mask'), 'scene masks:')
    for mask in scene.items(itype='mask'):
        h3dd.print_debug(f'mask: <{mask.name}> <{mask}>')
        if mask.channel('ptyp') is None:
            h3dd.print_debug('skipped: ptyp is None')
            continue
        if not is_material_ptyp(mask.channel('ptyp').get()):  # type:ignore
            h3dd.print_debug('skipped: ptyp is not "Material"')
            continue
        if mask.channel('ptag').get() == '':  # type:ignore
            h3dd.print_debug('skipped: ptag == ""')
            continue
        # add polygon tag name string to list
        material_str = '{}'.format(mask.channel('ptag').get())  # type:ignore
        materials_set.add(get_safe_material_str(name=material_str))
        h3dd.print_debug(
            'added to materials set - mask: <{}> material_str: <{}> get_safe_material_str(): <{}>'.
            format(mask.name, material_str, get_safe_material_str(material_str))
        )
    # add tags to the materials
    materials_set.update(tags)
    # remove Default tag to add it later at the start
    materials_set.remove(h3dc.DEFAULT_MATERIAL_ASSIGNMENT)
    # convert set to list
    materials = list(materials_set)
    # store materials list in user value
    materials.sort()
    # insert Default at the top of the materials list
    materials.insert(0, h3dc.DEFAULT_MATERIAL_ASSIGNMENT)
    materials_string_store = '\t'.join(materials)
    # create user value if not created
    if not is_defined_user_value(h3dc.USERVAL_NAME_MATERIALS_STORE):
        def_new_user_value(
            h3dc.USERVAL_NAME_MATERIALS_STORE, UV_TYPE_STRING, UV_LIFE_TEMPORARY
        )
    # store materials string
    set_user_value(h3dc.USERVAL_NAME_MATERIALS_STORE, materials_string_store)

    h3dd.print_items(materials, 'materials list output:')
    return materials


def get_safe_material_str(name):
    safe_name = name.replace(';', ';;')
    return safe_name


def restore_safe_material_str(safe_name):
    restored_name = safe_name.replace(';;', ';')
    return restored_name


def display_table(tags, materials, tags_materials_map, start):
    finish = start + PAGE_SIZE
    if finish > len(tags):
        finish = len(tags)
    # set desired page start
    set_page_start(tags=tags, start=finish - PAGE_SIZE)
    # get actual page start
    start = get_page_start()

    clear_table_ui()
    # remap table name update - colors count
    lx.eval('select.attr {93645054749:sheet} set')
    # get materials list size without dummy
    lx.eval('attr.label "remap table: {} material(s)"'.format(len(tags) - 1))

    for index in range(start, finish):
        build_line(
            ui_line=index - start + 1,
            map_index=index,
            tags=tags,
            materials=materials,
            tags_materials_map=tags_materials_map,
        )


def update_table(tags, start):
    # global tags_materials_map
    finish = start + PAGE_SIZE
    if finish > len(tags):
        finish = len(tags)

    if not is_defined_user_value(h3dc.USERVAL_NAME_MAP_STORE):
        print(
            'user.value {} not exist. Try scan scene first'.format(
                h3dc.USERVAL_NAME_MAP_STORE
            )
        )
        sys.exit()
    tags_materials_map_store_string = get_user_value(h3dc.USERVAL_NAME_MAP_STORE)
    tags_materials_map = [int(x) for x in tags_materials_map_store_string.split(';')]

    for index in range(start, finish):
        material_ui_id = get_material_ui(ui_line=index - start + 1)
        tags_materials_map[index] = int(material_ui_id)  # type:ignore

    tags_materials_map_store_string = ';'.join(
        ['{}'.format(x) for x in tags_materials_map]
    )  # compose string
    set_user_value(
        h3dc.USERVAL_NAME_MAP_STORE, tags_materials_map_store_string
    )  # store to config

    return tags_materials_map


def get_material_ui(ui_line):
    user_value_name_material = '{}{:03d}'.format(
        h3dc.USERVAL_NAME_MATERIAL_BASE, ui_line
    )
    if not is_defined_user_value(user_value_name_material):
        print(
            'get_material_ui(): User value <{}> not exist, return None'.format(
                user_value_name_material
            )
        )
        return None
    return get_user_value(user_value_name_material)


def clear_table_ui():
    """
    clear dynamic UI elements
    :return: None
    """
    # delete user values
    i = 0
    while True:
        user_value_name_color = '{}{:03d}'.format(h3dc.USERVAL_NAME_COLOR_BASE, i + 1)
        user_value_name_material = '{}{:03d}'.format(
            h3dc.USERVAL_NAME_MATERIAL_BASE, i + 1
        )
        if is_defined_user_value(user_value_name_color):
            delete_defined_user_value(user_value_name_color)
        else:
            break
        if is_defined_user_value(user_value_name_material):
            delete_defined_user_value(user_value_name_material)
        else:
            break
        i += 1
        if i > PAGE_SIZE:
            print('UI user value count max limit reached: {}'.format(PAGE_SIZE))
            break


def build_line(ui_line, map_index, tags, materials, tags_materials_map):
    user_value_name_color = '{}{:03d}'.format(h3dc.USERVAL_NAME_COLOR_BASE, ui_line)
    user_value_name_material = '{}{:03d}'.format(
        h3dc.USERVAL_NAME_MATERIAL_BASE, ui_line
    )
    # make new user value
    def_new_user_value(user_value_name_color, UV_TYPE_COLOR, UV_LIFE_TEMPORARY)
    # set color for UI element
    float_color_str = get_float_color_str_from_mask(tags[map_index])
    set_user_value(user_value_name_color, float_color_str)
    # select line with zero-based index
    lx.eval('select.attr {{93645054749:sheet/{}}} set'.format(ui_line - 1))
    cur_line = lx.eval('select.attr ?')
    # select line source tag element
    lx.eval(f'select.attr {{{cur_line}/{h3dc.SOURCE_TAG_ID}}} set')
    # assign tooltip to source tag element
    lx.eval(f'attr.tooltip "{map_index}: {{{tags[map_index]}}}"')
    # materials dropbox setup
    materials_list_string = ';'.join(['{}'.format(x) for x in range(len(materials))])
    materials_listnames_string = ';'.join(materials)
    lx.eval(
        f'user.def {{{h3dc.USERVAL_NAME_MATERIAL_DEFAULT}}} list "{{{materials_list_string}}}"'
    )
    lx.eval(
        'user.def {} listnames "{}"'.format(
            h3dc.USERVAL_NAME_MATERIAL_DEFAULT, materials_listnames_string
        )
    )
    def_new_user_value(user_value_name_material, UV_TYPE_INTEGER, UV_LIFE_TEMPORARY)
    lx.eval(
        'user.def {} list "{}"'.format(user_value_name_material, materials_list_string)
    )
    lx.eval(
        'user.def {} listnames "{}"'.format(
            user_value_name_material, materials_listnames_string
        )
    )
    lx.eval(
        'user.def {} attr:username value:{}'.format(
            user_value_name_material, tags[map_index]
        )
    )
    set_user_value(user_value_name_material, tags_materials_map[map_index])
    # select line target material element and assign tooltip
    lx.eval('select.attr {{{}/{}}} set'.format(cur_line, h3dc.TARGET_TAG_ID))
    lx.eval(
        'attr.tooltip "select material to replace <{}> tag"'.format(tags[map_index])
    )
    # select line select polygons command and assign tooltip
    lx.eval('select.attr {{{}/{}}} set'.format(cur_line, h3dc.SELECT_TAG_ID))
    lx.eval('attr.tooltip "select polygons for {} polygon tag"'.format(tags[map_index]))


def int_to_float_color(int_color):
    int_r, int_g, int_b = int_color.split(' ')
    float_r = int(int_r) / 255.0
    float_g = int(int_g) / 255.0
    float_b = int(int_b) / 255.0
    float_color = '{} {} {}'.format(float_r, float_g, float_b)
    return float_color


def get_sel_color_index(tags):
    selected = scene.selectedByType('mask')
    selected_colors = list()
    for mask in selected:
        if not mask.name.startswith(h3dc.COLOR_NAME_PREFIX):
            continue
        if mask.channel('ptyp') is None:
            continue
        if mask.channel('ptyp').get() != 'Material':
            continue
        if mask.channel('ptag').get() == '':
            continue
        selected_colors.append(get_color_str_from_name(name_str=mask.name))
    if len(selected_colors) < 1:
        return get_page_start()  # return previous index
    min_index = tags.index(selected_colors[0])
    for color in selected_colors:
        min_index = min(tags.index(color), min_index)
    return min_index


def get_color_str_from_name(name_str):
    # print('name_str:<{}>'.format(name_str))
    if h3dc.COLOR_NAME_PREFIX not in name_str:
        return name_str
    start_pos = len(h3dc.COLOR_NAME_PREFIX)
    end_pos = name_str.find(h3dc.MATERIAL_SUFFIX)
    # no ' (Material)' suffix found
    if end_pos < 0:
        # set end_pos to last char if no ' (Material)' suffix
        end_pos = len(name_str)
    return_str = name_str[start_pos:end_pos]
    return return_str


def scan_init(tags, materials):
    if not is_defined_user_value(h3dc.USERVAL_NAME_OVERSIZE):
        def_new_user_value(
            h3dc.USERVAL_NAME_OVERSIZE, UV_TYPE_STRING, UV_LIFE_TEMPORARY
        )
    if len(tags) - 1 <= PAGE_SIZE:
        set_user_value(h3dc.USERVAL_NAME_OVERSIZE, False)
    else:
        set_user_value(h3dc.USERVAL_NAME_OVERSIZE, True)
    set_page_start(tags=tags, start=1)
    tag_material_map = list()
    if not is_defined_user_value(h3dc.USERVAL_NAME_MATERIAL_DEFAULT):
        def_new_user_value(
            h3dc.USERVAL_NAME_MATERIAL_DEFAULT, UV_TYPE_INTEGER, UV_LIFE_TEMPORARY
        )
    set_user_value(h3dc.USERVAL_NAME_MATERIAL_DEFAULT, 0)
    # initiate tags_materials_map
    for i in range(1, len(tags)):
        # tag_material_map.append(i if i < materials_count else 0)
        tag_str = tags[i]
        try:
            material_id = materials.index(tag_str)
        except IndexError:
            material_id = 0
        tag_material_map.append(material_id)

    # first line [0] in tags_materials_map is default material assignment
    # add default material at the start
    tag_material_map.insert(
        0, 0
    )  # for default material (tags[0]) assigned material is materials[0] (Default)
    # store tags_materials_map
    tags_materials_map_store_string = ';'.join(
        ['{}'.format(x) for x in tag_material_map]
    )  # compose string
    if not is_defined_user_value(h3dc.USERVAL_NAME_MAP_STORE):
        def_new_user_value(
            h3dc.USERVAL_NAME_MAP_STORE, val_type='string', val_life='temporary'
        )
    set_user_value(
        h3dc.USERVAL_NAME_MAP_STORE, tags_materials_map_store_string
    )  # store to config

    return tag_material_map


def save_map(tags, materials, tags_materials_map):
    # prepare tags_materials_map (replace color indexes and material indexes by strings)
    map_lines = list()
    for color_id, material_id in enumerate(tags_materials_map):
        if color_id == 0:
            continue
        color_str = tags[color_id]
        if not color_str.startswith(h3dc.COLOR_NAME_PREFIX):
            continue
        color_str_num = color_str.replace(h3dc.COLOR_NAME_PREFIX, '')
        material_str = materials[material_id]
        if material_str.startswith(h3dc.COLOR_NAME_PREFIX):
            continue
        tags_materials_line = '{} - {}\n'.format(color_str_num, material_str)
        map_lines.append(tags_materials_line)
    # cancel save if map lines list empty
    if not len(map_lines):
        print('No data to save')
        sys.exit()
    scene_name = scene.name.split('.')[0].strip()
    if not scene_name or scene_name == '':
        scene_name = 'RGB - Materials'
    # get directory and file name (file save as dialog box)
    full_filename = modo.dialogs.customFile(
        'fileSave',
        'Save colors-materials map',
        ('text',),
        ('Text File',),
        ext=('txt',),
        path=scene_name,
    )
    # print('save_map()>dialog_result: <{}>'.format(dialog_result))
    if full_filename is None:
        sys.exit()
    # save decoded tags_materials_map to file
    with open(full_filename, 'w') as file:  # type:ignore
        file.writelines(map_lines)


def load_map(filename, tags, materials, tags_materials_map):
    # check tags_list
    if not len(tags):
        print('No CAD colors found, try scan the scene first')
        sys.exit()
    if filename is None:
        print('filename is None')
        return tags_materials_map
    # logging.debug('tags:<{}>'.format(tags))
    # read file data to tags_materials_map
    try:
        with open(filename, 'r') as file:
            map_lines = file.readlines()
    except IOError:
        print('IO Error for <{}> file'.format(filename))
        return tags_materials_map
    # read color and material from line
    for line in map_lines:
        if line.strip() == '':
            # skip void lines
            continue
        color_str_num, material_str = line.strip().split(' - ')
        color_str_num = color_str_num.strip()
        # clean numbers from multiple spaces
        color_str_num = ' '.join(
            list(
                s.strip().zfill(3) for s in color_str_num.split(' ') if s.strip() != ''
            )
        )
        color_str = h3dc.COLOR_NAME_PREFIX + color_str_num
        if color_str not in tags:
            # skip if no color found
            continue
        # get index of color_str in the tags_list
        color_id = tags.index(color_str)
        # get index of material_str in the materials_list
        if material_str not in materials:
            # skip if no materials found
            continue
        material_id = materials.index(material_str)
        # assign loaded material index to the tags_materials_map
        tags_materials_map[color_id] = material_id

    return tags_materials_map


def get_load_map_filename():
    # get directory and file name (file open dialog box)
    filename = modo.dialogs.customFile(
        'fileOpen', "Open colors-materials map", ("text",), ("Text File",), ('*.txt',)
    )
    return filename


def get_default_load_map_filename():
    config_default_filename = get_user_value(h3dc.USERVAL_NAME_DEF_MAP_PATH)
    if os.path.exists(config_default_filename):
        print('default map table path:<{}>'.format(config_default_filename))
        return config_default_filename
    kits_path = str(lx.eval('query platformservice path.path ? kits'))
    default_filename = os.path.join(
        kits_path, h3dc.KIT_NAME, h3dc.KIT_SCRIPTS_NAME, h3dc.MAP_DEFAULT_FILENAME
    )  # type:ignore
    if os.path.exists(default_filename):
        print('default map table path:<{}>'.format(default_filename))
        return default_filename
    lux_kits_path = kits_path.replace('\\Kits', '\\Luxology\\Kits')  # type:ignore
    default_filename = os.path.join(
        lux_kits_path, h3dc.KIT_NAME, h3dc.KIT_SCRIPTS_NAME, h3dc.MAP_DEFAULT_FILENAME
    )
    if os.path.exists(default_filename):
        print('default map table path:<{}>'.format(default_filename))
        return default_filename
    print('default map table path not found')
    return config_default_filename


def apply_command(tags, materials, tags_materials_map):
    selection_sets = dict()
    for source_id, target_id in enumerate(tags_materials_map):
        if source_id == 0:
            # skip [0] item
            continue
        if tags[source_id] == materials[target_id]:
            print('map_pair[{}] skipped'.format(source_id))
            # skip if source tag match with target tag
            continue
        select_polygons_by_tag(tags[source_id])
        lx.eval('select.createSet "{}"'.format(tags[source_id]))
        selection_sets[tags[source_id]] = materials[target_id]
        lx.eval('select.drop polygon')
    # select all mesh items
    scene.deselect()
    meshes = scene.items(itype=c.MESH_TYPE)
    for mesh in meshes:
        mesh.select(replace=False)
    lx.eval('select.type polygon')
    for source_tag, target_tag in selection_sets.items():
        lx.eval(f'select.pickWorkingSet {{{source_tag}}} true')
        lx.eval(f'select.pickWorkingSet {{{source_tag}}}')
        try:
            lx.eval('!!select.selectWorkingSet 2')
        except RuntimeError as error:
            print('select selection set <{}> error: {}'.format(source_tag, error))
            continue
        try:
            lx.eval('!!poly.setMaterial "{}"'.format(target_tag))
        except RuntimeError as error:
            print('{} replace by {}: {}'.format(source_tag, target_tag, error))

    lx.eval('select.drop polygon')
    lx.eval('select.type item')
    scene.deselect()


def get_float_color_str_from_mask(tag_name):
    color_str = h3dc.MISSING_COLOR
    for mask in scene.items(itype=c.MASK_TYPE):
        if mask.channel('ptyp') is None:
            continue
        if (
            mask.channel('ptyp').get() != 'Material'  # type:ignore
            and mask.channel('ptyp').get() != ''  # type:ignore
        ):
            continue
        if mask.channel('ptag').get() == '':  # type:ignore
            continue
        # filter out mismatched masks
        if mask.channel('ptag').get() != tag_name:  # type:ignore
            continue
        # find advancedMaterial in mask children
        for child in mask.children():
            if child.type == 'advancedMaterial':
                adv_mat = child
                # get diffuse color
                color_str = ' '.join(
                    str(x) for x in adv_mat.channel('diffCol').get()  # type: ignore
                )  # type:ignore
                return color_str

    return color_str


def select_polygons_by_tag(select_material_tag):
    is_mask_selected = False
    for mask in scene.items(itype=c.MASK_TYPE):
        if mask.channel('ptyp') is None:
            continue
        if not is_material_ptyp(mask.channel('ptyp').get()):  # type:ignore
            continue
        if mask.channel('ptag').get().replace(h3dc.MATERIAL_SUFFIX, '') == select_material_tag:  # type: ignore
            mask.select(replace=True)
            is_mask_selected = True
            break
    if is_mask_selected:
        lx.eval('material.selectPolygons')
        return
    tmp_mesh = scene.addMesh()
    tmp_mesh.select(replace=True)
    # add unit cube into current mesh item
    lx.eval('script.run "macro.scriptservice:32235710027:macro"')
    lx.eval(
        'poly.setMaterial "{}" {{0.6 0.6 0.6}} 0.8 0.04 true false false'.format(
            select_material_tag
        )
    )
    seaching_mask = scene.selectedByType(itype=c.MASK_TYPE)[0]
    scene.removeItems(tmp_mesh)
    seaching_mask.select(replace=True)
    lx.eval('material.selectPolygons')


def is_visible(item):
    visible = item.channel('visible').get()
    return visible == 'default' or visible == 'on'


def deselect_hidden():
    for mesh in scene.selectedByType(itype=c.MESH_TYPE):
        if not mesh.parents:
            if is_visible(mesh):
                continue
        else:
            if all([is_visible(item) for item in mesh.parents]) and is_visible(mesh):
                continue
        # deselect polygons
        mesh.geometry.polygons.select()
        mesh.deselect()


def main():
    print('')
    print('remap_table_UI.py start...')

    scene_filename = scene.filename
    if scene_filename is None:
        print('No active scene found, try open a scene first')
        sys.exit()

    # get remap table page size from config
    global PAGE_SIZE
    PAGE_SIZE = get_user_value(h3dc.USERVAL_NAME_PAGE_SIZE)

    args = lx.args()
    if not args:
        raise ValueError('Missing command argument')
    command = get_command(args)
    global_tags = get_tags_list(command=command)
    global_materials = get_materials_list(command=command, tags=global_tags)
    # clear previous table and user variables
    if command == CMD_SCAN:
        global_tags_materials_map = scan_init(
            tags=global_tags, materials=global_materials
        )
        global_tags_materials_map = load_map(
            filename=get_default_load_map_filename(),
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
        )
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=get_page_start(),
        )

    if command == CMD_PREV:
        global_tags_materials_map = update_table(
            tags=global_tags, start=get_page_start()
        )
        set_page_start(tags=global_tags, start=get_page_start() - PAGE_SIZE)
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=get_page_start(),
        )

    if command == CMD_NEXT:
        global_tags_materials_map = update_table(
            tags=global_tags, start=get_page_start()
        )
        set_page_start(tags=global_tags, start=get_page_start() + PAGE_SIZE)
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=get_page_start(),
        )

    if command == CMD_SAVE:
        global_tags_materials_map = update_table(
            tags=global_tags, start=get_page_start()
        )
        save_map(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
        )

    if command == CMD_LOAD:
        global_tags_materials_map = update_table(
            tags=global_tags, start=get_page_start()
        )
        global_tags_materials_map = load_map(
            filename=get_load_map_filename(),
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
        )
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=get_page_start(),
        )

    if command == CMD_APPLY:
        # update table to get all changes from UI
        global_tags_materials_map = update_table(
            tags=global_tags, start=get_page_start()
        )
        # assign mapped materials
        apply_command(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
        )
        # rescan scene to get updated state
        global_tags = get_tags_list(command=CMD_SCAN)
        global_materials = get_materials_list(command=CMD_SCAN, tags=global_tags)
        global_tags_materials_map = scan_init(
            tags=global_tags, materials=global_materials
        )
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=set_page_start(start=1, tags=global_tags),
        )

    if command == CMD_SELECT:
        arg_mode, line_id_str = lx.args()  # type:ignore
        line_id = int(line_id_str)
        tag_id = int(line_id) + get_page_start() - 1
        select_polygons_by_tag(global_tags[tag_id])
        deselect_hidden()

    if command == CMD_CREATE_MISSING_MATS:
        for tag in global_tags:
            select_polygons_by_tag(tag)
        lx.eval('select.drop polygon')
        modo.Scene().deselect()

    print('remap_table_UI.py done.')


if __name__ == '__main__':
    PAGE_SIZE = 0
    scene = modo.Scene()
    h3dd = H3dDebug(enable=False, file=replace_file_ext(scene.filename, '.log'))
    main()

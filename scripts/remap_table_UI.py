#!/usr/bin/python
# ================================
# (C)2021-2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# materials remap modo UI (color material map)
# remap_table_UI v1.12

import modo
import lx
import os.path
import modo.constants as c
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
import h3d_utils as h3du
from h3d_debug import H3dDebug
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
import h3d_kit_constants as h3dc


def get_page_start():
    page_start = h3du.get_user_value(h3dc.USERVAL_NAME_PAGE_START)
    return page_start


def set_page_start(start, tags):
    if start >= len(tags):
        start = len(tags) - 1
    if start < 1:
        start = 1
    h3du.set_user_value(h3dc.USERVAL_NAME_PAGE_START, start)
    return get_page_start()


def read_args():
    mode = h3dc.RM_SCAN
    arg_command = lx.args()[0]
    if arg_command == '-prev':
        mode = h3dc.RM_PREV
    elif arg_command == '-next':
        mode = h3dc.RM_NEXT
    elif arg_command == '-scan':
        mode = h3dc.RM_SCAN
    elif arg_command == '-save':
        mode = h3dc.RM_SAVE
    elif arg_command == '-load':
        mode = h3dc.RM_LOAD
    elif arg_command == '-apply':
        mode = h3dc.RM_APPLY
    elif arg_command == '-select':
        mode = h3dc.RM_SELECT
    else:
        print('Unknown argument(s):', lx.args())
    return mode


def get_tags_list(mode):
    # colors = list()
    tags = list()
    if mode == h3dc.RM_SCAN:
        # get material tag from mesh polygons
        for mesh in modo.scene.current().items(itype=c.MESH_TYPE):
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
        if not lx.eval('query scriptsysservice userValue.isDefined ? {}'.format(h3dc.USERVAL_NAME_COLORS_STORE)):
            lx.eval('user.defNew {} type:string life:temporary'.format(h3dc.USERVAL_NAME_COLORS_STORE))
        # store colors string
        h3du.set_user_value(h3dc.USERVAL_NAME_COLORS_STORE, colors_string_store)

    else:
        # read colors list from user value
        try:
            colors_string_store = h3du.get_user_value(h3dc.USERVAL_NAME_COLORS_STORE)
            tags.extend(colors_string_store.split(';'))
        except RuntimeError:
            print('The scene is not scanned. Press the <scan scene> button to scan.')
            exit()
    if len(tags) < 1 or (len(tags) == 1 and tags[0] == ''):
        print('Void tags list. Try to scan scene or run Consolidate CAD Materials script first.')
        exit()
    return tags


def get_materials_list(mode, tags):
    materials_set = set()
    if mode == h3dc.RM_SCAN:
        for mask in modo.scene.current().items(itype='mask'):
            if mask.channel('ptyp') is None:
                continue
            if mask.channel('ptyp').get() != 'Material':
                continue
            if mask.channel('ptag').get() == '':
                continue
            # add polygon tag name string to list
            material_str = '{}'.format(mask.channel('ptag').get())
            materials_set.add(get_safe_material_str(name=material_str))
        # add tags to the materials
        materials_set.update(tags)
        # remove Default tag  to add it later at the start
        materials_set.remove(h3dc.DEFAULT_MATERIAL_ASSIGNMENT)
        # convert set to list
        materials = list(materials_set)
        # store materials list in user value
        materials.sort()
        # insert Default at the top of the materials list
        materials.insert(0, h3dc.DEFAULT_MATERIAL_ASSIGNMENT)
        materials_string_store = '\t'.join(materials)
        # create user value if not created
        if not lx.eval('query scriptsysservice userValue.isDefined ? {}'.format(h3dc.USERVAL_NAME_MATERIALS_STORE)):
            lx.eval('user.defNew {} type:string life:temporary'.format(h3dc.USERVAL_NAME_MATERIALS_STORE))
        # store materials string
        h3du.set_user_value(h3dc.USERVAL_NAME_MATERIALS_STORE, materials_string_store)
    else:
        # read materials list from user value
        materials_string_store = h3du.get_user_value(h3dc.USERVAL_NAME_MATERIALS_STORE)
        materials = list(materials_string_store.split('\t'))

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
            tags_materials_map=tags_materials_map
        )


def update_table(tags, start):
    # global tags_materials_map
    finish = start + PAGE_SIZE
    if finish > len(tags):
        finish = len(tags)

    if not lx.eval('query scriptsysservice userValue.isDefined ? {}'.format(h3dc.USERVAL_NAME_MAP_STORE)):
        print('user.value {} not exist. Try scan scene first'.format(h3dc.USERVAL_NAME_MAP_STORE))
        exit()
    tags_materials_map_store_string = h3du.get_user_value(h3dc.USERVAL_NAME_MAP_STORE)
    tags_materials_map = [int(x) for x in tags_materials_map_store_string.split(';')]

    for index in range(start, finish):
        material_ui_id = get_material_ui(ui_line=index - start + 1)
        tags_materials_map[index] = int(material_ui_id)

    tags_materials_map_store_string = ';'.join(['{}'.format(x) for x in tags_materials_map])  # compose string
    h3du.set_user_value(h3dc.USERVAL_NAME_MAP_STORE, tags_materials_map_store_string)  # store to config

    return tags_materials_map


def get_material_ui(ui_line):
    user_value_name_material = '{}{:03d}'.format(h3dc.USERVAL_NAME_MATERIAL_BASE, ui_line)
    if not lx.eval('query scriptsysservice userValue.isDefined ? {}'.format(user_value_name_material)):
        print('get_material_ui(): User value <{}> not exist, return None'.format(user_value_name_material))
        return None
    return h3du.get_user_value(user_value_name_material)


def clear_table_ui():
    """
    clear dynamic UI elements
    :return: None
    """
    # delete user values
    i = 0
    while True:
        user_value_name_color = '{}{:03d}'.format(h3dc.USERVAL_NAME_COLOR_BASE, i + 1)
        user_value_name_material = '{}{:03d}'.format(h3dc.USERVAL_NAME_MATERIAL_BASE, i + 1)
        if lx.eval('query scriptsysservice userValue.isDefined ? {}'.format(user_value_name_color)):
            lx.eval('!user.defDelete {}'.format(user_value_name_color))  # delete existing user value
        else:
            break
        if lx.eval('query scriptsysservice userValue.isDefined ? {}'.format(user_value_name_material)):
            lx.eval('!user.defDelete {}'.format(user_value_name_material))  # delete existing user value
        else:
            break
        i += 1
        if i > PAGE_SIZE:
            print('UI user value count max limit reached: {}'.format(PAGE_SIZE))
            break


def build_line(ui_line, map_index, tags, materials, tags_materials_map):
    user_value_name_color = '{}{:03d}'.format(h3dc.USERVAL_NAME_COLOR_BASE, ui_line)
    user_value_name_material = '{}{:03d}'.format(h3dc.USERVAL_NAME_MATERIAL_BASE, ui_line)
    # make new user value
    lx.eval('user.defNew {} type:color life:temporary'.format(user_value_name_color))
    # set color for UI element
    float_color_str = get_float_color_str_from_mask(tags[map_index])
    h3du.set_user_value(user_value_name_color, float_color_str)
    # select line with zero-based index
    lx.eval('select.attr {{93645054749:sheet/{}}} set'.format(ui_line - 1))
    cur_line = lx.eval('select.attr ?')
    # select line source tag element
    lx.eval('select.attr {{{}/{}}} set'.format(cur_line, h3dc.SOURCE_TAG_ID))
    # assign tooltip to source tag element
    lx.eval('attr.tooltip "{}: {}"'.format(map_index, tags[map_index]))
    # materials dropbox setup
    materials_list_string = ';'.join(['{}'.format(x) for x in range(len(materials))])
    materials_listnames_string = ';'.join(materials)
    lx.eval('user.def {} list "{}"'.format(h3dc.USERVAL_NAME_MATERIAL_DEFAULT, materials_list_string))
    lx.eval('user.def {} listnames "{}"'.format(h3dc.USERVAL_NAME_MATERIAL_DEFAULT, materials_listnames_string))
    lx.eval('user.defNew {} type:integer life:temporary'.format(user_value_name_material))
    lx.eval('user.def {} list "{}"'.format(user_value_name_material, materials_list_string))
    lx.eval('user.def {} listnames "{}"'.format(user_value_name_material, materials_listnames_string))
    lx.eval('user.def {} attr:username value:{}'.format(user_value_name_material, tags[map_index]))
    h3du.set_user_value(user_value_name_material, tags_materials_map[map_index])
    # select line target material element and assign tooltip
    lx.eval('select.attr {{{}/{}}} set'.format(cur_line, h3dc.TARGET_TAG_ID))
    lx.eval('attr.tooltip "select material to replace <{}> tag"'.format(tags[map_index]))
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
    selected = modo.scene.current().selectedByType('mask')
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
    if not lx.eval('query scriptsysservice userValue.isDefined ? {}'.format(h3dc.USERVAL_NAME_OVERSIZE)):
        lx.eval('user.defNew {} type:boolean life:temporary'.format(h3dc.USERVAL_NAME_OVERSIZE))
    if len(tags) - 1 <= PAGE_SIZE:
        h3du.set_user_value(h3dc.USERVAL_NAME_OVERSIZE, False)
    else:
        h3du.set_user_value(h3dc.USERVAL_NAME_OVERSIZE, True)
    set_page_start(tags=tags, start=1)
    tag_material_map = list()
    if not lx.eval('query scriptsysservice userValue.isDefined ? {}'.format(h3dc.USERVAL_NAME_MATERIAL_DEFAULT)):
        lx.eval('user.defNew {} type:integer life:temporary'.format(h3dc.USERVAL_NAME_MATERIAL_DEFAULT))
    h3du.set_user_value(h3dc.USERVAL_NAME_MATERIAL_DEFAULT, 0)
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
    tag_material_map.insert(0, 0)  # for default material (tags[0]) assigned material is materials[0] (Default)
    # store tags_materials_map
    tags_materials_map_store_string = ';'.join(['{}'.format(x) for x in tag_material_map])  # compose string
    if not lx.eval('query scriptsysservice userValue.isDefined ? {}'.format(h3dc.USERVAL_NAME_MAP_STORE)):
        lx.eval('user.defNew {} type:string life:temporary'.format(h3dc.USERVAL_NAME_MAP_STORE))
    h3du.set_user_value(h3dc.USERVAL_NAME_MAP_STORE, tags_materials_map_store_string)  # store to config

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
        exit()
    scene_name = modo.scene.current().name.split('.')[0].strip()
    if not scene_name or scene_name == '':
        scene_name = 'RGB - Materials'
    # get directory and file name (file save as dialog box)
    full_filename = modo.dialogs.customFile(
        'fileSave',
        'Save colors-materials map',
        ('text',),
        ('Text File',),
        ext=('txt',),
        path=scene_name
    )
    # print('save_map()>dialog_result: <{}>'.format(dialog_result))
    if full_filename is None:
        exit()
    # save decoded tags_materials_map to file
    with open(full_filename, 'w') as file:
        file.writelines(map_lines)


def load_map(filename, tags, materials, tags_materials_map):
    # check tags_list
    if not len(tags):
        print('No CAD colors found, try scan the scene first')
        exit()
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
        color_str_num = ' '.join(list(
            s.strip().zfill(3) for s in color_str_num.split(' ') if s.strip() != ''
        ))
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
        'fileOpen',
        'Open colors-materials map',
        ('text',),
        ('Text File',),
        ('*.txt',)
    )
    return filename


def get_default_load_map_filename():
    config_default_filename = h3du.get_user_value(h3dc.USERVAL_NAME_DEF_MAP_PATH)
    if os.path.exists(config_default_filename):
        print('default map table path:<{}>'.format(config_default_filename))
        return config_default_filename
    kits_path = lx.eval('query platformservice path.path ? kits')
    default_filename = os.path.join(kits_path, h3dc.KIT_NAME, h3dc.KIT_SCRIPTS_NAME, h3dc.MAP_DEFAULT_FILENAME)
    if os.path.exists(default_filename):
        print('default map table path:<{}>'.format(default_filename))
        return default_filename
    lux_kits_path = kits_path.replace('\\Kits', '\\Luxology\\Kits')
    default_filename = os.path.join(lux_kits_path, h3dc.KIT_NAME, h3dc.KIT_SCRIPTS_NAME, h3dc.MAP_DEFAULT_FILENAME)
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
    modo.scene.current().deselect()
    meshes = modo.scene.current().items(itype=c.MESH_TYPE)
    for mesh in meshes:
        mesh.select(replace=False)
    lx.eval('select.type polygon')
    for source_tag, target_tag in selection_sets.items():
        lx.eval('select.pickWorkingSet "{}" true'.format(source_tag))
        lx.eval('select.pickWorkingSet "{}"'.format(source_tag))
        lx.eval('select.selectWorkingSet 2')
        try:
            lx.eval('!!poly.setMaterial "{}"'.format(target_tag))
        except RuntimeError as error:
            print('{} replace by {}: {}'.format(source_tag, target_tag, error))

    lx.eval('select.drop polygon')
    lx.eval('select.type item')
    modo.scene.current().deselect()


def get_float_color_str_from_mask(tag_name):
    # h3dd.print_debug("get_float_color_str_from_mask('{}')".format(tag_name))
    color_str = h3dc.MISSING_COLOR
    for mask in modo.scene.current().items(itype=c.MASK_TYPE):
        if mask.channel('ptyp') is None:
            # h3dd.print_debug("ptyp is None", 1)
            continue
        if mask.channel('ptyp').get() != 'Material' and mask.channel('ptyp').get() != '':
            # h3dd.print_debug("ptyp <{}> != Material".format(mask.channel('ptyp').get()), 1)
            continue
        if mask.channel('ptag').get() == '':
            # h3dd.print_debug("ptag == ''", 1)
            continue
        # filter out mismatched masks
        if mask.channel('ptag').get() != tag_name:
            # h3dd.print_debug("ptag <{}> != tag_name <{}>".format(mask.channel('ptag').get(), tag_name), 1)
            continue
        # find advancedMaterial in mask children
        h3dd.print_debug("ptag <{}> == tag_name <{}>".format(mask.channel('ptag').get(), tag_name), 1)
        for child in mask.children():
            if child.type == 'advancedMaterial':
                adv_mat = child
                # get diffuse color
                color_str = ' '.join(str(x) for x in adv_mat.channel('diffCol').get())
                # h3dd.print_debug("advancedMaterial: color_str <{}>".format(color_str))
                return color_str

    # h3dd.print_debug("return color_str: <{}>".format(color_str))
    return color_str


def select_polygons_by_tag(select_material_tag):
    for mask in modo.scene.current().items(itype=c.MASK_TYPE):
        if mask.channel('ptyp') is None:
            continue
        if not h3du.is_material_ptyp(mask.channel('ptyp').get()):
            continue
        if mask.channel('ptag').get().replace(h3dc.MATERIAL_SUFFIX, '') == select_material_tag:
            mask.select(replace=True)
            # h3dd.print_debug('<{}> polygon tag selected'.format(select_material_tag))
            break
    lx.eval('material.selectPolygons')


def is_visible(item):
    visible = item.channel('visible').get()
    return visible == 'default' or visible == 'on'


def deselect_hidden():
    for mesh in modo.Scene().selectedByType(itype=c.MESH_TYPE):

        h3dd.print_debug("mesh: <{}> visible: <{}>, visible channel: <{}>"
                         .format(mesh.name, is_visible(mesh), mesh.channel('visible').get()))
        if all([is_visible(item) for item in mesh.parents]) and is_visible(mesh):
            continue

        for item in mesh.parents:
            h3dd.print_debug('parent <{}>: is_visible = {}'.format(item.name, is_visible(item)), 1)

        mesh.geometry.polygons.select()
        mesh.deselect()


def main():
    print('')
    print('remap_table_UI.py start...')

    scene_filename = modo.scene.current().filename
    if scene_filename is None:
        print('No active scene found, try open a scene first')
        exit()

    # get remap table page size from config
    global PAGE_SIZE
    PAGE_SIZE = h3du.get_user_value(h3dc.USERVAL_NAME_PAGE_SIZE)

    run_mode = read_args()
    global_tags = get_tags_list(mode=run_mode)
    global_materials = get_materials_list(mode=run_mode, tags=global_tags)
    # clear previous table and user variables
    if run_mode == h3dc.RM_SCAN:
        global_tags_materials_map = scan_init(tags=global_tags, materials=global_materials)
        global_tags_materials_map = load_map(
            filename=get_default_load_map_filename(),
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map
        )
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=get_page_start())

    if run_mode == h3dc.RM_PREV:
        global_tags_materials_map = update_table(tags=global_tags, start=get_page_start())
        set_page_start(tags=global_tags, start=get_page_start() - PAGE_SIZE)
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=get_page_start())

    if run_mode == h3dc.RM_NEXT:
        global_tags_materials_map = update_table(tags=global_tags, start=get_page_start())
        set_page_start(tags=global_tags, start=get_page_start() + PAGE_SIZE)
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=get_page_start())

    if run_mode == h3dc.RM_SAVE:
        global_tags_materials_map = update_table(tags=global_tags, start=get_page_start())
        save_map(tags=global_tags, materials=global_materials, tags_materials_map=global_tags_materials_map)

    if run_mode == h3dc.RM_LOAD:
        global_tags_materials_map = update_table(tags=global_tags, start=get_page_start())
        global_tags_materials_map = load_map(
            filename=get_load_map_filename(),
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map)
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=get_page_start())

    if run_mode == h3dc.RM_APPLY:
        # update table to get all changes from UI
        global_tags_materials_map = update_table(tags=global_tags, start=get_page_start())
        # assign mapped materials
        apply_command(tags=global_tags, materials=global_materials, tags_materials_map=global_tags_materials_map)
        # rescan scene to get updated state
        global_tags = get_tags_list(mode=h3dc.RM_SCAN)
        global_materials = get_materials_list(mode=h3dc.RM_SCAN, tags=global_tags)
        global_tags_materials_map = scan_init(tags=global_tags, materials=global_materials)
        display_table(
            tags=global_tags,
            materials=global_materials,
            tags_materials_map=global_tags_materials_map,
            start=set_page_start(start=1, tags=global_tags))

    if run_mode == h3dc.RM_SELECT:
        arg_mode, line_id_str = lx.args()
        line_id = int(line_id_str)
        tag_id = int(line_id) + get_page_start() - 1
        select_polygons_by_tag(global_tags[tag_id])
        deselect_hidden()

    print('remap_table_UI.py done.')


if __name__ == '__main__':
    PAGE_SIZE = 0
    h3dd = H3dDebug(enable=False, file=h3du.replace_file_ext(modo.Scene().filename, ".log"))
    main()

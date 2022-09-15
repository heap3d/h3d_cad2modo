#!/usr/bin/python
# ================================
# (C)2021 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# materials remap modo UI

import modo
import lx
import os.path

scene = modo.scene.current()
material_name_prefix = '#auto# '
default_material_assignment = 'default'
premap_filename = 'RGB Materials.txt'
runtime_map_basename = 'h3d_cmm_runtime.txt'
material_suffix = ' (Material)'
color_base = 'h3d_cmm_color'
material_base = 'h3d_cmm_material'
userval_page_start = 'h3d_cmm_page_start'
page_size = 10

rm_prev = 1
rm_next = 2
rm_save = 3
rm_scan = 4
rm_load = 5
rm_find = 6


def get_scene_dir():
    return os.path.splitext(scene.filename)[0]


def get_runtime_map_filename():
    return '{}\\{}'.format(get_scene_dir(), runtime_map_basename)


def get_color_map_filename():
    return ''.format()


def get_colors_count():
    return len(colors_list)


def get_page_start():
    return lx.eval('user.value {} ?'.format(userval_page_start))


def set_page_start(start=0):
    if start < 0:
        start = 0
    if start > get_colors_count():
        start = get_colors_count()-1
    lx.eval('user.value {} {}'.format(userval_page_start, start))


def get_pretable_map():
    return dict()


def get_table_map():
    return dict()


def normalise_color_name(name):
    return name


def read_args():
    mode = rm_scan
    for arg in lx.args():
        print('arg:', arg)
        if arg.startswith('-prev'):
            mode = rm_prev
        elif arg.startswith('-next'):
            mode = rm_next
        elif arg.startswith('-scan'):
            mode = rm_scan
        elif arg.startswith('-save'):
            mode = rm_save
        elif arg.startswith('-load'):
            mode = rm_load
        elif arg.startswith('-find'):
            mode = rm_find
        else:
            print('Unknown argument(s):', lx.args())
    return mode


def get_color_list():
    colors = list()
    for mask in scene.items(itype='mask'):
        if not mask.name.startswith(material_name_prefix):
            continue
        if mask.channel('ptyp') is None:
            continue
        if mask.channel('ptyp').get() != 'Material':
            continue
        if mask.channel('ptag').get() == '':
            continue
        # add color string to list
        colors.append(get_color_str(mask.name))
    return colors


def get_material_list():
    materials = list()
    materials.append(default_material_assignment)
    for mask in scene.items(itype='mask'):
        if mask.name.startswith(material_name_prefix):
            continue
        if mask.channel('ptyp') is None:
            continue
        if mask.channel('ptyp').get() != 'Material':
            continue
        if mask.channel('ptag').get() == '':
            continue
        # add material name string to list
        material_str = '{}'.format(mask.name)
        materials.append(material_str)
    return materials


def display_table(start=0):
    finish = start + page_size
    if finish > get_colors_count():
        finish = get_colors_count()
    set_page_start(finish - page_size)
    start = get_page_start()
    print('display_table: start=', start, 'finish=', finish-1, 'colors in scene:', len(colors_list))
    for index in range(start, finish):
        print('item #', index)
        build_line(ui_line=index-start+1, color_index=index, material_index=0)


def build_line(ui_line=1, color_index=0, material_index=0):
    print('[{}]: <{}> --> <{}>'.format(ui_line, colors_list[color_index], material_list[material_index]))
    lx.eval('user.def h3d_cmm_color{:03d}'.format(ui_line))


def get_sel_color_index():
    selected = scene.selectedByType('mask')
    selected_colors = list()
    for mask in selected:
        if not mask.name.startswith(material_name_prefix):
            continue
        if mask.channel('ptyp') is None:
            continue
        if mask.channel('ptyp').get() != 'Material':
            continue
        if mask.channel('ptag').get() == '':
            continue
        selected_colors.append(get_color_str(mask.name))
    # print 'selected colors:', selected_colors, len(selected_colors)
    if len(selected_colors) < 1:
        # print 'return previous index:', get_page_start()
        return get_page_start()  # return previous index
    min_index = colors_list.index(selected_colors[0])
    # print 'min_index initialisation:', min_index
    for color in selected_colors:
        min_index = min(colors_list.index(color), min_index)
    # print 'selected index:', min_index
    return min_index


def get_color_str(name_str):
    start_pos = len(material_name_prefix)
    end_pos = name_str.find(material_suffix)
    if end_pos == 0:  # no ' (Material)' suffix found
        end_pos = len(name_str)  # set end_pos to last char if no ' (Material)' suffix
    return name_str[start_pos:end_pos]


def clear_table():
    pass


print()
print('start...')

run_mode = read_args()
colors_list = get_color_list()
material_list = get_material_list()
# print colors_list
# print material_list

# TODO clear previous table and user variables
if run_mode == rm_scan:
    set_page_start(0)
    display_table(get_page_start())
if run_mode == rm_prev:
    set_page_start(get_page_start()-page_size)
    display_table(get_page_start())
if run_mode == rm_next:
    set_page_start(get_page_start()+page_size)
    display_table(get_page_start())
if run_mode == rm_find:
    set_page_start(get_sel_color_index())
    display_table(get_page_start())

print('done.')

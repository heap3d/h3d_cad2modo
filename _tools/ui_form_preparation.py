#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# materials remap modo UI (color material map) config file preparation
"""
modo command examples:
attr.addCommand "@{D:/work/scripts/modo/h3d tools/h3d_cad2modo/scripts/remap_table_UI.py} -next"
attr.label "select polygons"
attr.enable false
attr.tooltip "select polygons for specific polygon tag"
attr.formFilterCommand "user.value h3d_rtu_color001 ?"
attr.parent {65340891386:sheet} 0
"""
import modo
import lx

UI_RANGE = 300
USER_VALUE_COLOR_BASE = 'h3d_rtu_color'

SELECT_TAG_ID = 0
SOURCE_TAG_ID = 1
TARGET_TAG_ID = 2

scene = modo.scene.current()

for i in range(UI_RANGE):
    lx.eval('select.attr {{93645054749:sheet/{}}} set'.format(i))
    cur_line = lx.eval('select.attr ?')
    # lx.eval('attr.enable true')
    # lx.eval('attr.formJustification justified')
    # num_str = str(i + 1).zfill(3)
    # lx.eval('attr.formFilterCommand "user.value {}{} ?"'.format(USER_VALUE_COLOR_BASE, num_str))
    # lx.eval('attr.label "line {}"'.format(num_str))

    # lx.eval('select.attr {{{}/{}}} set'.format(cur_line, SOURCE_TAG_ID))
    # lx.eval('attr.showLabel false')
    # lx.eval('attr.controlCommand "user.value h3d_rtu_color{} ?"'.format(num_str))

    # lx.eval('select.attr {{{}/{}}} set'.format(cur_line, TARGET_TAG_ID))
    # lx.eval('attr.showLabel false')
    # lx.eval('attr.controlCommand "user.value h3d_rtu_material{} ?"'.format(num_str))

    # lx.eval('select.attr {{93645054749:sheet/{}}} set'.format(i))
    # lx.eval('attr.addCommand "@{{scripts/remap_table_UI.py}} -select -{}"'.format(num_str))
    lx.eval('select.attr {{{}/{}}} set'.format(cur_line, SELECT_TAG_ID))
    select_line = lx.eval('select.attr ?')
    select_hash = select_line[:-2]
    print(select_hash)
    lx.eval('attr.parent {{{}}} 0'.format(select_hash))
    # lx.eval('attr.label "select polygons"')
    # lx.eval('attr.tooltip "select polygons for specific polygon tag"')

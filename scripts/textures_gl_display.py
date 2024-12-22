#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# set texture GL Display
# ================================

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_debug import prints, fn_in, fn_out, h3dd

ALL_ON = 'on'
ALL_OFF = 'off'
SELECTED_ON = 'selon'
SELECTED_OFF = 'seloff'
ALL_TOGGLE = 'toggle'
SEL_TOGGLE = 'seltoggle'


def main():
    actions = {
        ALL_ON: all_on_action,
        ALL_OFF: all_off_action,
        SELECTED_ON: selected_on_action,
        SELECTED_OFF: selected_off_action,
        ALL_TOGGLE: all_toggle_action,
        SEL_TOGGLE: selected_toggle_action,
    }
    args = lx.args()
    if not args:
        arg = ALL_ON
    else:
        arg = args[0]

    action = actions.get(arg, all_on_action)
    # selected = modo.Scene().selected
    # prints(selected)
    action()
    # restore selection
    # modo.Scene().deselect()
    # for item in selected:
    #     item.select()


def all_on_action():
    fn_in()
    textures = modo.Scene().items(itype=c.IMAGEMAP_TYPE)
    prints(textures)
    turn_on_gl_display(textures)
    fn_out()


def all_off_action():
    fn_in()
    textures = modo.Scene().items(itype=c.IMAGEMAP_TYPE)
    prints(textures)
    turn_off_gl_display(textures)
    fn_out()


def selected_on_action():
    fn_in()
    textures = modo.Scene().selectedByType(itype=c.IMAGEMAP_TYPE)
    prints(textures)
    turn_on_gl_display(textures)
    fn_out()


def selected_off_action():
    fn_in()
    textures = modo.Scene().selectedByType(itype=c.IMAGEMAP_TYPE)
    prints(textures)
    turn_off_gl_display(textures)
    fn_out()


def all_toggle_action():
    fn_in()
    textures = modo.Scene().items(itype=c.IMAGEMAP_TYPE)
    prints(textures)
    toggle_gl_display(textures)
    fn_out()


def selected_toggle_action():
    fn_in()
    textures = modo.Scene().selectedByType(itype=c.IMAGEMAP_TYPE)
    prints(textures)
    toggle_gl_display(textures)
    fn_out()


def turn_on_gl_display(textures: list[modo.Item]):
    fn_in()
    prints(textures)
    # modo.Scene().deselect()
    for item in textures:
        # item.select()
        lx.eval(f'item.channel textureLayer$gldisp true item:{{{item.id}}}')
    fn_out()


def turn_off_gl_display(textures: list[modo.Item]):
    fn_in()
    prints(textures)
    # modo.Scene().deselect()
    for item in textures:
        # item.select()
        lx.eval(f'item.channel textureLayer$gldisp false item:{{{item.id}}}')
    fn_out()


def toggle_gl_display(textures: list[modo.Item]):
    fn_in()
    prints(textures)
    # modo.Scene().deselect()
    for item in textures:
        # item.select()
        lx.eval(f'item.channel textureLayer$gldisp ?+ item:{{{item.id}}}')
    fn_out()


if __name__ == '__main__':
    h3dd.enable_debug_output(False)
    main()

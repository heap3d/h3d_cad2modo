#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get default map table path
# ================================

import lx
import modo
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
import h3d_utils as h3du
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
import h3d_kit_constants as h3dc


def main():
    # initialize filename
    filename = h3du.get_user_value(h3dc.USERVAL_NAME_DEF_MAP_PATH)

    dialog_result = modo.dialogs.fileOpen(ftype='text', path=filename)
    if dialog_result:
        h3du.set_user_value(h3dc.USERVAL_NAME_DEF_MAP_PATH, dialog_result)


if __name__ == '__main__':
    main()

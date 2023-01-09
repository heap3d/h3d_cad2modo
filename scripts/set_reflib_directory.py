#!/usr/bin/python
# ================================
# (C)2022-2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get directory
# ================================

import lx
import modo
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
import h3d_utils as h3du
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
import h3d_kit_constants as h3dc


def main():
    # initialize dir_path
    filename = h3du.get_user_value(h3dc.USER_VAL_REFLIB_DIR_NAME)

    dialog_result = modo.dialogs.dirBrowse(title='Select Reference Library Directory', path=filename)
    if dialog_result:
        h3du.set_user_value(h3dc.USER_VAL_REFLIB_DIR_NAME, dialog_result)


if __name__ == '__main__':
    main()

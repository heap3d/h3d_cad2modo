#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get image filename
# ================================

import lx
import modo
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
from h3d_utils import H3dUtils
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
import h3d_kit_constants as h3dc


def main():
    # initialize filename
    filename = h3du.get_user_value(h3dc.USER_VAL_NAME_ENV_PATH_NAME)

    dialog_result = modo.dialogs.fileOpen(ftype='image', path=filename)
    if dialog_result:
        h3du.set_user_value(h3dc.USER_VAL_NAME_ENV_PATH_NAME, dialog_result)


h3du = H3dUtils()

if __name__ == '__main__':
    main()

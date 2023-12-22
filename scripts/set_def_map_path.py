#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get default map table path
# ================================

import modo

from h3d_utilites.scripts.h3d_utils import get_user_value, set_user_value

import h3d_cad2modo.scripts.h3d_kit_constants as h3dc


def main():
    print('')
    print('set_def_map_path.py start...')
    # initialize filename
    filename = get_user_value(h3dc.USERVAL_NAME_DEF_MAP_PATH)

    dialog_result = modo.dialogs.fileOpen(ftype='text', path=filename)
    if dialog_result:
        set_user_value(h3dc.USERVAL_NAME_DEF_MAP_PATH, dialog_result)

    print('set_def_map_path.py done.')


if __name__ == '__main__':
    main()

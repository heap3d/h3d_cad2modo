#!/usr/bin/python
# ================================
# (C)2022-2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get directory
# ================================

import modo

from h3d_utilites.scripts.h3d_utils import get_user_value, set_user_value

import h3d_cad2modo.scripts.h3d_kit_constants as h3dc


def main():
    print('')
    print('set_reflib_directory.py start...')

    # initialize dir_path
    filename = get_user_value(h3dc.USER_VAL_REFLIB_DIR_NAME)

    dialog_result = modo.dialogs.dirBrowse(title='Select Reference Library Directory', path=filename)
    if dialog_result:
        set_user_value(h3dc.USER_VAL_REFLIB_DIR_NAME, dialog_result)

    print('set_reflib_directory.py done.')


if __name__ == '__main__':
    main()

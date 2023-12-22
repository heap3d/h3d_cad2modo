#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get image filename
# ================================

import modo

from h3d_utilites.scripts.h3d_utils import get_user_value, set_user_value

import h3d_cad2modo.scripts.h3d_kit_constants as h3dc


def main():
    print('')
    print('set_filename.py start...')

    # initialize filename
    filename = get_user_value(h3dc.USER_VAL_NAME_ENV_PATH_NAME)

    dialog_result = modo.dialogs.fileOpen(ftype='image', path=filename)
    if dialog_result:
        set_user_value(h3dc.USER_VAL_NAME_ENV_PATH_NAME, dialog_result)

    print('set_filename.py done.')


if __name__ == '__main__':
    main()

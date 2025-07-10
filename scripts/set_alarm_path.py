#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# set alarm path
# ================================

import modo

from h3d_utilites.scripts.h3d_utils import get_user_value, set_user_value

from scripts.mesh_islands_cleanup import USERVAL_ALARM_SOUND_PATH


def main():
    print('')
    print('Setting alarm path start...')

    # initialize dir_path
    filename = get_user_value(USERVAL_ALARM_SOUND_PATH)

    dialog_result = modo.dialogs.fileOpen(ftype='', title="Specify alarm path", path=filename)
    if dialog_result:
        set_user_value(USERVAL_ALARM_SOUND_PATH, dialog_result)

    print('Setting alarm path done.')


if __name__ == "__main__":
    main()

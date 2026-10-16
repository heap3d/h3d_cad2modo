#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select control item by user value

import modo

from h3d_utilites.scripts.h3d_utils import (
    get_user_value,
    select_if_exists,
)

from h3d_cad2modo.scripts.h3d_kit_constants import USERVAL_NAME_CONTROL_ITEM
from h3d_cad2modo.scripts.add_and_link_channel_to_control import define_user_values


def main():
    define_user_values()
    control_name = get_user_value(USERVAL_NAME_CONTROL_ITEM)
    try:
        control = modo.Scene().item(control_name)
    except:
        control = None
    if not control:
        modo.dialogs.alert('Select Control', 'No Control detected. Please set an item as Control')
        return

    select_if_exists((control,))


if __name__ == '__main__':
    main()

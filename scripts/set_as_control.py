#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# set last selected item as control to add channels

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import set_user_value

from h3d_cad2modo.scripts.h3d_kit_constants import USERVAL_NAME_CONTROL_ITEM

ALERT_TITLE = 'Set As Control'


def main():
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)

    if not selected:
        modo.dialogs.alert(ALERT_TITLE, 'Please select the item you want to set as the control.')

    control_item: modo.Item = selected[-1]
    set_user_value(USERVAL_NAME_CONTROL_ITEM, control_item.name)


if __name__ == '__main__':
    main()

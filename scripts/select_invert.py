#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select items in the scene by name regex
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import select_if_exists


def main():
    selected_item = set(modo.Scene().selectedByType(c.LOCATOR_TYPE, superType=True))
    all_items = set(modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True))

    select_if_exists(all_items - selected_item)


if __name__ == '__main__':
    main()

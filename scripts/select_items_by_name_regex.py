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

from h3d_utilites.scripts.h3d_utils import get_user_value

from scripts.select_meshes_by_name_regex import get_by_name_regex_from


USERVAL_REGEX_PATTERN = 'h3d_smbn_regex'


def main():
    pattern = get_user_value(USERVAL_REGEX_PATTERN)
    items_all = get_items(modo.Scene())
    items_filtered = get_by_name_regex_from(items_all, pattern)

    modo.Scene().deselect()
    for item in items_filtered:
        item.select()


def get_items(scene: modo.Scene) -> list[modo.Item]:
    return [item for item in scene.items(itype=c.LOCATOR_TYPE, superType=True)]


if __name__ == '__main__':
    main()

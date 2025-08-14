#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# remove empty group locators in the scene
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import itype_str


def main():
    group_locators = modo.Scene().items(c.GROUPLOCATOR_TYPE)
    remove_locators = [
        loc
        for loc in group_locators
        if is_empty_group_loc(loc)
    ]

    modo.Scene().deselect()
    for locator in remove_locators:
        try:
            modo.Scene().removeItems(locator)
        except RuntimeError:
            print(f"Failed to remove locator: {locator.name}")
            continue


def is_empty_group_loc(locator: modo.Item) -> bool:
    if not locator:
        raise ValueError("Locator is not provided")

    non_group_locator_type_children = [
        loc
        for loc in locator.children(recursive=True)
        if loc.type != itype_str(c.GROUPLOCATOR_TYPE)
    ]

    if non_group_locator_type_children:
        return False

    return True


if __name__ == '__main__':
    main()

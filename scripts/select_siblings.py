#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select items at the same level of hierarchy as the selected
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import get_user_value, is_visible

from h3d_cad2modo.scripts.h3d_kit_constants import USERVAL_IGNORE_HIDDEN


def main():
    ignore_hidden = bool(get_user_value(USERVAL_IGNORE_HIDDEN))
    if ignore_hidden:
        selected = get_selected_visible()
    else:
        selected = get_selected()

    modo.Scene().deselect()

    for item in selected:
        parent = item.parent
        if not parent:
            item.select()
            continue

        if ignore_hidden:
            children = get_children_visible(parent)
        else:
            children = parent.children()

        for child in children:
            child.select()


def get_selected() -> list[modo.Item]:
    return modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)


def get_selected_visible() -> list[modo.Item]:
    return [
        i
        for i in modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
        if is_visible(i)
    ]


def get_children_visible(item: modo.Item) -> list[modo.Item]:
    if not item:
        return []
    
    return [i for i in item.children() if is_visible(i)]


if __name__ == '__main__':
    main()

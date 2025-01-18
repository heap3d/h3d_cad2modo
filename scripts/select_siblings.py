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
    visible_only = bool(get_user_value(USERVAL_IGNORE_HIDDEN))
    selected = get_selected(visible_only)
    root_children = get_root_children(visible_only)

    similar_children: set[modo.Item] = set()

    for item in selected:
        if item in similar_children:
            continue
        parent = item.parent
        if not parent:
            children = root_children
        else:
            children = get_children(parent, visible_only)

        for child in children:
            if child in similar_children:
                continue
            similar_children.add(child)

    for item in similar_children:
        item.select()


def get_selected(visible: bool) -> list[modo.Item]:
    if visible:
        return [
            i
            for i in modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
            if is_visible(i)
        ]
    else:
        return modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)


def get_children(item: modo.Item, visible: bool) -> list[modo.Item]:
    if not item:
        return []

    if visible:
        return [i for i in item.children() if is_visible(i)]
    else:
        return item.children()


def get_root_children(visible: bool) -> list[modo.Item]:
    if visible:
        return [
            item
            for item in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
            if item.parent is None and is_visible(item)
        ]
    else:
        return [
            item
            for item in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
            if item.parent is None
        ]


if __name__ == '__main__':
    main()

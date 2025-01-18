#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select items same type at the same level of hierarchy as the selected
# ================================

import modo

from h3d_utilites.scripts.h3d_utils import get_user_value

from h3d_cad2modo.scripts.h3d_kit_constants import USERVAL_IGNORE_HIDDEN
from h3d_cad2modo.scripts.select_siblings import get_selected, get_children, get_root_children


def main():
    visible_only = bool(get_user_value(USERVAL_IGNORE_HIDDEN))
    selected = get_selected(visible_only)
    root_children = get_root_children(visible_only)
    selected_types = set([item.type for item in selected])

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
            if child.type in selected_types:
                similar_children.add(child)

    for item in similar_children:
        item.select()


if __name__ == '__main__':
    main()

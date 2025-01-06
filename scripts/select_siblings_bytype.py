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
from h3d_cad2modo.scripts.select_siblings import get_selected, get_selected_visible, get_children_visible


def main():
    ignore_hidden = bool(get_user_value(USERVAL_IGNORE_HIDDEN))
    if ignore_hidden:
        selected = get_selected_visible()
    else:
        selected = get_selected()
    selected_types = set([item.type for item in selected])

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
            if child.type in selected_types:
                child.select()


if __name__ == '__main__':
    main()

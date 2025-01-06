#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select items at the same level of hierarchy as the selected, filtered by name
# ================================

import re

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
            is_similar = is_name_similar(child.name, item.name)
            if is_similar:
                child.select()


def is_name_similar(name: str, template: str) -> bool:
    strip_pattern = r'(.*?) ?[ _(]?\d+\)?$'

    template_match = re.match(strip_pattern, template)
    if not template_match:
        template_stripped = template
    else:
        template_stripped = template_match.group(1)

    name_match = re.match(strip_pattern, name)
    if not name_match:
        name_sripped = name
    else:
        name_sripped = name_match.group(1)

    if template_stripped.strip() == name_sripped.strip():
        return True

    return False


if __name__ == '__main__':
    main()

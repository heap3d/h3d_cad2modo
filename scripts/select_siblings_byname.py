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
from h3d_cad2modo.scripts.select_siblings import get_selected, get_children, get_root_children


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
            is_similar = is_name_similar(child.name, item.name)
            if is_similar:
                similar_children.add(child)

    for item in similar_children:
        item.select()


def is_name_similar(name: str, template: str, regex_pattern: str = '') -> bool:
    if not regex_pattern:
        # default strip_pattern for modo copies naming: item (2); item(2); item 2; item_2; item2
        # strip_pattern = r'^(.*?)[ _(\d\)]*$'
        regex_pattern = r'^(.*?)[._ (d)]*[ ().\d]*\d*\)?$'

    template_match = re.match(regex_pattern, template)
    if not template_match:
        template_stripped = template
    else:
        template_stripped = template_match.group(1)

    name_match = re.match(regex_pattern, name)
    if not name_match:
        name_sripped = name
    else:
        name_sripped = name_match.group(1)

    if template_stripped.strip() == name_sripped.strip():
        return True

    return False


if __name__ == '__main__':
    main()

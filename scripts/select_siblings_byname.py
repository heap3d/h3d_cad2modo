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

from h3d_cad2modo.scripts.h3d_kit_constants import USERVAL_IGNORE_HIDDEN, REGEX_PATTERN
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


def is_name_similar(name: str, template: str, regex_pattern=REGEX_PATTERN) -> bool:
    template_match = re.search(regex_pattern, template)

    if not template_match:
        template_stripped = template
    else:
        if template_match.groups():
            template_stripped = template_match.group(1)
        else:
            start, end = template_match.span()
            template_stripped = template[start:end]

    name_match = re.search(regex_pattern, name)

    if not name_match:
        name_sripped = name
    else:
        if name_match.groups():
            name_sripped = name_match.group(1)
        else:
            start, end = name_match.span()
            name_sripped = name[start:end]

    if template_stripped.strip() == name_sripped.strip():
        return True

    return False


if __name__ == '__main__':
    main()

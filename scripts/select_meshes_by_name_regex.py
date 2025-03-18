#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select meshes in the scene by name regex
# ================================

import re
import modo

from h3d_utilites.scripts.h3d_utils import get_user_value

from h3d_cad2modo.scripts.select_deformable_meshes import get_meshes


USERVAL_REGEX_PATTERN = 'h3d_smbn_regex'


def main():
    pattern = get_user_value(USERVAL_REGEX_PATTERN)
    items = get_meshes(modo.Scene())
    meshes = get_by_name_regex_from(items, pattern)

    modo.Scene().deselect()
    for mesh in meshes:
        mesh.select()


def get_by_name_regex_from(items: list[modo.Item], pattern: str) -> list[modo.Item]:
    return [
        item
        for item in items
        if is_match(item.name, pattern)
    ]


def is_match(name: str, pattern: str) -> bool:
    matches = re.match(pattern, name)
    if not matches:
        return False

    return True


if __name__ == '__main__':
    main()

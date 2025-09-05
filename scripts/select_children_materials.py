#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select children materials for selected masks

from typing import Iterable

import modo
import modo.constants as c

MATERIAL_TYPES = ['advancedMaterial',]


def main():
    items = modo.Scene().selectedByType(itype=c.MASK_TYPE)
    materials = get_materials(items)

    modo.Scene().deselect()
    for m in materials:
        m.select()


def get_materials(masks: Iterable[modo.Item]) -> set[modo.Item]:
    materials = set()
    for item in masks:
        materials.update([m for m in item.children(recursive=True) if m.type in MATERIAL_TYPES])

    return materials


if __name__ == "__main__":
    main()

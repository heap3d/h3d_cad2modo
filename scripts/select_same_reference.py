#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select all items from same imported reference
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import select_if_exists


def main():
    selected_references: list[modo.Item] = [
        item
        for item in modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
        if is_reference_item(item)
    ]

    reference_ids = {get_reference_id(item) for item in selected_references}

    reference_items = [
        item
        for item in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
        if is_reference_item(item)
    ]

    matched_references = [
        item
        for item in reference_items
        if get_reference_id(item) in reference_ids
    ]

    modo.Scene().deselect()
    select_if_exists(matched_references)


def get_reference_id(item: modo.Item) -> str:
    if not is_reference_item(item):
        raise ValueError(f'Item "{item.name}" is not from reference')

    return item.id.split(':')[0]


def is_reference_item(item: modo.Item) -> bool:
    if ':' not in item.id:
        return False

    return True


def is_same_reference(item: modo.Item, reference_id: str) -> bool:
    if not is_reference_item(item):
        return False

    return get_reference_id(item) == reference_id


if __name__ == '__main__':
    main()

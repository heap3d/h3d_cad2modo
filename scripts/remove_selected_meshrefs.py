#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# remove selected mesh references

from typing import Iterable

import modo


def main():
    selected: list[modo.Item] = modo.Scene().selectedByType(itype='locator', superType=True)

    is_running = True
    while is_running:
        childless = get_childless_children(selected)

        for item in childless[:1]:
            safe_remove_item(item)

        is_running = len(childless) > 0

    for item in selected:
        safe_remove_item(item)


def get_childless_children(items: Iterable[modo.Item]) -> list[modo.Item]:
    childless: list[modo.Item] = []
    for item in items:
        childless.extend([child for child in item.children(recursive=True) if not child.children()])
    return childless


def zero_len(item) -> int:
    if not item:
        return 0
    return len(item)


def safe_remove_item(item: modo.Item):
    try:
        modo.Scene().item(item.name)
        modo.Scene().removeItems(item)
    except LookupError:
        print(f'Item deleting error: {item.name}')


if __name__ == '__main__':
    main()

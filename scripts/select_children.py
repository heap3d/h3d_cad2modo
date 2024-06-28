#!/usr/bin/python
# ================================
# (C)2023-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select children recursive for selected items
# ================================

import modo


def main():
    scene = modo.Scene()
    items = scene.selected
    for item in items:
        if item.children():
            for child in item.children(recursive=True):
                child.select()


if __name__ == '__main__':
    main()

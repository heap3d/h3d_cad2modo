#!/usr/bin/python
# ================================
# (C)2019-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select texture locators
# ================================

import modo


def main():
    scene = modo.Scene()
    items = scene.selected
    for item in items:
        try:
            forwards = item.itemGraph('shadeLoc').forward()
            if not isinstance(forwards, list):
                continue
            for i in forwards:
                i.select()
        except LookupError:
            pass


if __name__ == '__main__':
    main()

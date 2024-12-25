#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select items same type at the same level of hierarchy as the selected
# ================================

import modo
import modo.constants as c


def main():
    selected: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    selected_types = set([item.type for item in selected])

    modo.Scene().deselect()

    for item in selected:
        parent = item.parent
        if not parent:
            item.select()
            continue
        children = parent.children()
        for child in children:
            if child.type in selected_types:
                child.select()


if __name__ == '__main__':
    main()

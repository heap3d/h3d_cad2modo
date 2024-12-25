#!/usr/bin/python
# ================================
# (C)2023-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select parent for selected items
# ================================

import modo
import modo.constants as c


def main():
    selected: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)

    modo.Scene().deselect()

    for item in selected:
        parent = item.parent
        if not parent:
            item.select()
        else:
            parent.select()


if __name__ == '__main__':
    main()

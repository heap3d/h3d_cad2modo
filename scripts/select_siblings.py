#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select sibling items for the selected
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_debug import prints


def main():
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    prints(selected)


if __name__ == '__main__':
    main()

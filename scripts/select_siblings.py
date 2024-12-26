#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select items at the same level of hierarchy as the selected
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import get_user_value


USERVAL_IGNORE_HIDDEN = 'h3d_set_ignore_hidden'


def main():
    ignore_hidden = get_user_value(USERVAL_IGNORE_HIDDEN)
    selected: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)

    modo.Scene().deselect()

    for item in selected:
        parent = item.parent
        if not parent:
            item.select()
            continue
        children = [i for i in parent.children() if not is_hidden(i)]
        for child in children:
            child.select()


def is_hidden(item: modo.Item) -> bool:
    ...


if __name__ == '__main__':
    main()

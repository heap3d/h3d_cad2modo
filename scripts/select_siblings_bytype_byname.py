#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select items same type at the same level of hierarchy as the selected, filtered by name
# ================================

import modo
import modo.constants as c

from h3d_cad2modo.scripts.select_siblings_byname import is_name_similar


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
            is_similar = (child.type in selected_types) and is_name_similar(child.name, item.name)
            if is_similar:
                child.select()


if __name__ == '__main__':
    main()

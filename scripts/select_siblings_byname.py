#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select items at the same level of hierarchy as the selected, filtered by name
# ================================

import re

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_debug import h3dd, prints


def main():
    selected: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)

    modo.Scene().deselect()

    for item in selected:
        parent = item.parent
        if not parent:
            item.select()
            continue
        children = parent.children()
        for child in children:
            is_similar = is_name_similar(child.name, item.name)
            if is_similar:
                child.select()


def is_name_similar(name: str, template: str) -> bool:
    strip_pattern = r'(.*?) ?[ _(]?\d+\)?$'
    prints(name)
    prints(template)
    prints(strip_pattern)

    template_match = re.match(strip_pattern, template)
    prints(template_match)
    if not template_match:
        template_stripped = template
    else:
        template_stripped = template_match.group(1)

    name_match = re.match(strip_pattern, name)
    prints(name_match)
    if not name_match:
        name_sripped = name
    else:
        name_sripped = name_match.group(1)

    prints(template_stripped)
    prints(name_sripped)
    prints(template_stripped == name_sripped)
    if template_stripped.strip() == name_sripped.strip():
        return True

    return False


if __name__ == '__main__':
    h3dd.enable_debug_output(False)
    main()

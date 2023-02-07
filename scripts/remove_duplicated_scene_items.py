#!/usr/bin/python
# ================================
# (C)2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# remove duplicated scene items (FX items in Shader Tree)

import modo
import modo.constants as c
import lx


def main():
    scene_items = modo.Scene().items(itype=c.SCENE_TYPE)
    # remove all scene items except first one
    for scene_item in scene_items[1:]:
        modo.Scene().removeItems(scene_item)

    lx.eval('select.subItem {} set'.format(modo.Scene().renderItem.id))


if __name__ == '__main__':
    main()

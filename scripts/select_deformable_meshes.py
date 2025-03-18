#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select deformable meshes in the scene
# ================================

import modo
import modo.constants as c


def main():
    items = get_meshes(modo.Scene())
    meshes = get_deformable_from(items)

    if not meshes:
        return

    modo.Scene().deselect()
    for mesh in meshes:
        mesh.select()


def get_meshes(scene: modo.Scene) -> list[modo.Item]:
    MESHTYPES = (
        'mesh',
        'meshInst',
    )

    return [
        item
        for item in scene.items(itype=c.LOCATOR_TYPE, superType=True)
        if item.type in MESHTYPES
    ]


def get_deformable_from(items: list[modo.Item]) -> list[modo.Item]:
    return [
        item
        for item in items
        if is_deformable(item)
    ]


def get_nondeformable_from(items: list[modo.Item]) -> list[modo.Item]:
    return [
        item
        for item in items
        if not is_deformable(item)
    ]


def is_deformable(mesh: modo.Item) -> bool:
    if not mesh.itemGraph('deformers').reverse():
        return False

    return True


if __name__ == '__main__':
    main()

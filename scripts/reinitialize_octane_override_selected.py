#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# re-initiate octane override selected nodes
# ================================


import modo

from h3d_cad2modo.scripts.reinitialize_octane_override import reinitialize_octane_override
from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import replace_file_ext


def main():
    selected = scene.selected
    children = selected[:]

    for item in selected:
        if item.children():
            children = children + item.children(recursive=True)

    nodes = [item for item in children if item.type == 'material.octaneRenderer']

    for node in nodes:
        reinitialize_octane_override(node)


if __name__ == '__main__':
    scene = modo.Scene()
    log_name = replace_file_ext(scene.name)
    h3dd = H3dDebug(enable=False, file=log_name)

    main()

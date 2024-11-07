#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select schematic nodes for selected items
# ================================


import modo
import lx


class NodeSelection():
    ADD = 'add'
    SET = 'set'
    REMOVE = 'remove'
    TOGGLE = 'toggle'


def select_schematic_nodes(items: list[modo.Item], mode: str = NodeSelection.ADD) -> None:
    for item in items:
        schematic_node = item.itemGraph('schmItem').forward()[-1]  # type: ignore
        evalstr = f'select.node {{{schematic_node.id}}} {mode} {{{schematic_node.id}}}'
        print(evalstr)
        lx.eval(evalstr)


def main():
    selected_items = modo.Scene().selected
    select_schematic_nodes(selected_items)


if __name__ == '__main__':
    main()

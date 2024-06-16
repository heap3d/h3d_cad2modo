#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# remove items sets
# removes temporary item sets
# <alt> removes all item sets


import lx
from h3d_item_replace_tools.scripts.h3d_kit_constants import SELECTION_SET_BASE_NAME
from h3d_item_replace_tools.scripts.get_polygons_operations import remove_item_selection_set


ARG_ALL = 'all'


def remove_temporary_itemsets():
    remove_itemsets(SELECTION_SET_BASE_NAME)


def remove_all_itemsets():
    remove_itemsets()


def remove_itemsets(basename: str = ''):
    itemsets_indexes: list[int] = lx.eval("query layerservice itmsets ?")  # type: ignore
    if not itemsets_indexes:
        return

    itemsets = []
    for i in itemsets_indexes:
        itemset: str = lx.eval("query layerservice itmset.name ? %s" % i)  # type: ignore
        itemsets.append(itemset)

    filtered_itemsets = filter(lambda s: s.startswith(basename), itemsets)
    for itemset in filtered_itemsets:
        remove_item_selection_set(itemset)


def main():
    args = lx.args()
    if not args:
        remove_temporary_itemsets()
        return

    if ARG_ALL in args:
        remove_all_itemsets()


if __name__ == '__main__':
    main()

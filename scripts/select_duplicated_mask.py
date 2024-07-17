#!/usr/bin/python
# ================================
# (C)2020-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# select duplicated material mask, keep topmost unselected
# ================================

import modo
import lx

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import get_ptag_type, get_item_mask, get_ptag


COMPARE_BY_MATERIAL_TAG = False
COMPARE_BY_SELECTION_SET_TAG = False
COMPARE_BY_PART_TAG = False
COMPARE_BY_ITEM_MASK = False
COMPARE_BY_ALL = False
CLEAR_SELECTION = False
DELETE_MATERIAL_MASK = False

CBL_ALL = 'all'
CBL_MATERIAL = 'material'
CBL_SELECTION_SET = 'selection set'
CBL_PART = 'part'
CBL_ITEM_MASK = 'item mask'

# comparedBy user.value
USERVAL_COMPAREBY_NAME = 'h3d_select_duplicated_compareBy'
USERVAL_COMPAREBY_USERNAME = 'select duplicated material mask by'
USERVAL_COMPAREBY_DIALOGNAME = 'choose selection filter'
USERVAL_COMPAREBY_LIST = f'{CBL_ALL};{CBL_ITEM_MASK};{CBL_MATERIAL};{CBL_SELECTION_SET};{CBL_PART}'
# clear_selection user.value
USERVAL_CLEAR_SELECTION_NAME = 'h3d_select_duplicated_clear_selection'
USERVAL_CLEAR_SELECTION_USERNAME = 'clear selection'
USERVAL_CLEAR_SELECTION_DIALOGNAME = 'turn ON to clear selection'

# delete_material_mask user.value
USERVAL_DELETE_MATERIAL_MASK_NAME = 'H3D_SELECT_DUPLICATED_DELETE_MATERIAL_MASK'
USERVAL_DELETE_MATERIAL_MASK_USERNAME = 'delete material mask'
USERVAL_DELETE_MATERIAL_MASK_DIALOGNAME = 'turn ON to delete material mask'


def get_mask_list():
    mtag_mask_list = []
    if COMPARE_BY_MATERIAL_TAG:
        # include mask with Polygon Tag Type <Material> only and polygon tag not <(all)>
        for mask_item in scene.renderItem.children(True, 'mask'):
            tag_type = mask_item.channel('ptyp').get()  # type: ignore
            mtag = mask_item.channel('ptag').get()  # type: ignore
            if tag_type == 'Material' or tag_type == '':
                if mtag != '(none)' and mtag != '':
                    mtag_mask_list.append(mask_item)
    else:
        mtag_mask_list = scene.renderItem.children(True, 'mask')
    return mtag_mask_list


def are_mask_equal(mask1, mask2):
    printd(f'comparing <{mask1.name}> vs <{mask2.name}>...', 2)
    childrens1 = len(mask1.children(recursive=False, itemType='mask'))
    if childrens1 != 0:
        printd('childrens1 != 0: Not Equal', 3)
        return False
    childrens2 = len(mask2.children(recursive=False, itemType='mask'))
    if childrens2 != 0:
        printd('childrens2 != 0: Not Equal', 3)
        return False
    if get_item_mask(mask1) == get_item_mask(mask2):
        printd('identical item mask', 3)
        if get_ptag_type(mask1) == get_ptag_type(mask2):
            printd('identical ptag type', 3)
            if get_ptag(mask1) == get_ptag(mask2):
                printd('identical ptag', 3)
                printd('Equal', 3)
                return True
            else:
                printd('non-identical ptag', 3)
        else:
            printd('non-identical ptag type', 3)
    else:
        printd('non-identical item mask', 3)
    printd('Not Equal', 3)
    return False


def main():
    print('')
    print('start select_duplicated_mask.py ...')

    try:

        # keep top mask unselected
        duplicated_mask_list = set()
        # processed_tag_list = {}
        scene_mask_list = get_mask_list()
        tmp_scene_list = set(scene_mask_list)
        printi(scene_mask_list, 'scene_mask_list:')
        printi(tmp_scene_list, 'tmp_scene_list:')
        printd('scene_mask_list loop:')
        for mask in scene_mask_list:
            h3dd.print_debug(f'mask: {mask.name}', 1)
            if mask in tmp_scene_list:
                tmp_scene_list.remove(mask)
                printd(f'<{mask.name}> removed from tmp_scene_list', 1)
            processed_list = set(tmp_scene_list)
            printd('processed_list loop:', 1)
            for compared_mask in processed_list:
                if are_mask_equal(mask, compared_mask):
                    tmp_scene_list.remove(compared_mask)
                    duplicated_mask_list.add(compared_mask)
                    printd(f'dublicated mask detected: <{compared_mask.name}>, 2')
        # clear selection
        scene.deselect()
        # select duplicated masks
        for mask in duplicated_mask_list:
            mask.select()
        if len(duplicated_mask_list) > 0:
            lx.eval('item.editorColor yellow')
    except LookupError:
        print('Error found.')
    finally:
        print('')
        print('select_duplicated_mask.py done.')


if __name__ == '__main__':
    scene = modo.Scene()
    h3dd = H3dDebug(enable=False, file=scene.name + '.log')
    printd = h3dd.print_debug
    printi = h3dd.print_items

    main()

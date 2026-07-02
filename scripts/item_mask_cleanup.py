#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# cleaning up shader tree root masks for item shader group
# ================================

import modo
import modo.constants as c
import lx

from h3d_utilites.scripts.h3d_utils import itype_str, get_item_mask

from h3d_utilites.scripts.h3d_debug import h3dd, prints, fn_in, fn_out


RECYCLED_MASK_NAME = '--- DELETE ME ---'
RECYCLED_MASK_COLOR = 'red'
CLEANED_MASK_NAME = 'CLEANED MASKS'
CLEANED_MASK_COLOR = 'lightgreen'



def main():
    fn_in()
    shader_tree_masks = modo.Scene().items(itype=c.MASK_TYPE)
    prints(shader_tree_masks)
    root_masks = [mask for mask in shader_tree_masks if is_root_mask(mask)]
    prints(root_masks)
    item_masks = [mask for mask in root_masks if is_item_mask(mask)]
    prints(item_masks)

    if not item_masks:
        prints("No item masks found in the scene")
        fn_out()
        return

    recycled_group = create_mask(RECYCLED_MASK_NAME)
    recycled_group.select(replace=True)
    lx.eval(f'item.editorColor {RECYCLED_MASK_COLOR}')
    lx.eval(f'shader.setVisible "{recycled_group.id}" false')

    cleaned_group = create_mask(CLEANED_MASK_NAME)
    cleaned_group.select(replace=True)
    lx.eval(f'item.editorColor {CLEANED_MASK_COLOR}')

    for item_mask in item_masks:
        prints(item_mask)
        tag_masks = item_mask.children(itemType=c.MASK_TYPE)
        prints(tag_masks)
        for tag_mask in tag_masks:
            prints(tag_mask)
            tag_mask.setParent(cleaned_group)
        item_mask.setParent(recycled_group)

    recycled_group.select(replace=True)

    fn_out()


def is_root_mask(mask: modo.Item) -> bool:
    parent = mask.parent
    if not parent:
        raise ValueError(f"Mask {mask.name} has no parent")

    prints(f'parent.type: {parent.type}')
    prints(f'c.POLYRENDER_TYPE: {itype_str(c.POLYRENDER_TYPE)}')

    return parent.type == itype_str(c.POLYRENDER_TYPE)


def is_item_mask(mask: modo.Item) -> bool:
    fn_in()
    prints(mask)
    prints(f'Item mask name: {mask.name}')
    prints(f'Item mask value: {get_item_mask(mask)}')
    fn_out()

    return get_item_mask(mask) != '(all)'


def create_mask(name: str) -> modo.Item:
    render_item = get_render_item()
    render_item.select(replace=True)
    lx.eval('shader.create mask')
    lx.eval(f'item.name "{name}" mask')

    return modo.Scene().selectedByType(itype=c.MASK_TYPE)[0]


def get_render_item() -> modo.Item:
    render_items = modo.Scene().items(itype=c.POLYRENDER_TYPE)
    if not render_items:
        raise ValueError("No render item found in the scene")
    return render_items[0]


if __name__ == "__main__":
    h3dd.enable_debug_output()
    main()

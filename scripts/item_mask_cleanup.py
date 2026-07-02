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


RECYCLED_MASK_NAME = '--- DELETE ME ---'
RECYCLED_MASK_COLOR = 'red'
CLEANED_MASK_NAME = 'CLEANED MASKS'
CLEANED_MASK_COLOR = 'lightgreen'



def main():
    shader_tree_masks = modo.Scene().items(itype=c.MASK_TYPE)
    root_masks = [mask for mask in shader_tree_masks if is_root_mask(mask)]
    item_masks = [mask for mask in root_masks if is_item_mask(mask)]

    if not item_masks:
        print("No item masks found in the scene")
        return

    recycled_group = create_mask(RECYCLED_MASK_NAME, color=RECYCLED_MASK_COLOR, visible=False)
    cleaned_group = create_mask(CLEANED_MASK_NAME, color=CLEANED_MASK_COLOR)
    _ = [process_item_mask(mask, cleaned_group, recycled_group) for mask in item_masks]

    recycled_group.select(replace=True)
    print(f'{len(item_masks)} item masks processed')


def is_root_mask(mask: modo.Item) -> bool:
    parent = mask.parent
    if not parent:
        raise ValueError(f"Mask {mask.name} has no parent")

    return parent.type == itype_str(c.POLYRENDER_TYPE)


def is_item_mask(mask: modo.Item) -> bool:
    return get_item_mask(mask) != '(all)'


def create_mask(name: str, color='', visible=True) -> modo.Item:
    get_render_item().select(replace=True)
    lx.eval('shader.create mask')
    lx.eval(f'item.name "{name}" mask')

    if color:
        lx.eval(f'item.editorColor {color}')

    if not visible:
        lx.eval(f'shader.setVisible "{name}" false')

    return modo.Scene().selectedByType(itype=c.MASK_TYPE)[0]


def get_render_item() -> modo.Item:
    render_items = modo.Scene().items(itype=c.POLYRENDER_TYPE)
    if not render_items:
        raise ValueError("No render item found in the scene")
    return render_items[0]


def process_item_mask(item_mask: modo.Item, cleaned_group: modo.Item, recycled_group: modo.Item):
    tag_masks = item_mask.children(itemType=c.MASK_TYPE)
    for tag_mask in tag_masks:
        tag_mask.setParent(cleaned_group)
    item_mask.setParent(recycled_group)


if __name__ == "__main__":
    main()

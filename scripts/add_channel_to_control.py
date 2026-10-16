#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# adding selected channel from selected item to user channel of a specified control item

import modo

from h3d_utilites.scripts.h3d_utils import (
    get_user_value,
    select_if_exists,
)

from h3d_cad2modo.scripts.h3d_kit_constants import USERVAL_NAME_CONTROL_ITEM

from h3d_cad2modo.scripts.add_and_link_channel_to_control import (
    get_channel_selection,
    get_channel_item,
    recompile_nospaces,
    get_channel_name,
    get_channel_mode,
    get_channel_type,
    create_user_channel,
    define_user_values,
)


ALERT_TITLE = 'Add Channel To Control'
CONTROL_CHANNEL_PREFIX = 'acc_'


def main():
    channels = get_channel_selection()
    if not channels:
        modo.dialogs.alert(ALERT_TITLE, 'No selected channels detected')
        return

    define_user_values()
    control_name = get_user_value(USERVAL_NAME_CONTROL_ITEM)

    try:
        control = modo.Scene().item(control_name)
    except:
        control = None
    if not control:
        modo.dialogs.alert(ALERT_TITLE, 'No Control detected. Please set an item as Control')
        return

    items: set[modo.Item] = set()
    for channel in channels:
        channel_item = get_channel_item(channel)
        to_item: modo.Item = channel.item # type: ignore
        connected_items: list[modo.Item] = to_item.itemGraph('xfrmCore').forward() # type: ignore
        items.update(connected_items) # type: ignore
        itemname_nospaces = recompile_nospaces(channel_item.id)
        name = f'{CONTROL_CHANNEL_PREFIX}{itemname_nospaces}_{get_channel_name(channel)}'
        username = f'{connected_items[0].name} {get_channel_name(channel)}'
        mode = get_channel_mode(channel)
        ch_type = get_channel_type(channel)

        try:
            create_user_channel(control, name, username, mode, ch_type)
        except RuntimeError:
            print(f'Error creating and linking channels for <{channel}> Possible dublication, skipped.')

    select_if_exists(items)


if __name__ == '__main__':
    main()

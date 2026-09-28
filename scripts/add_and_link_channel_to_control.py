#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# adding selected channel from selected item to user channel of a specified control item

from typing import Union, Optional
import re

import lx
import modo

from h3d_utilites.scripts.h3d_utils import get_user_value

from h3d_cad2modo.scripts.h3d_kit_constants import USERVAL_NAME_CONTROL_ITEM


CHANNEL = Union[modo.Channel, modo.ChannelTriple]

ALERT_TITLE = 'Add Channel To Control'
CONTROL_CHANNEL_PREFIX = 'acc_'


def main():
    channels = get_channel_selection()
    if not channels:
        modo.dialogs.alert(ALERT_TITLE, 'No selected channels detected')
        return

    control_name = get_user_value(USERVAL_NAME_CONTROL_ITEM)

    try:
        control = modo.Scene().item(control_name)
    except:
        control = None
    if not control:
        modo.dialogs.alert(ALERT_TITLE, 'No Control detected. Please set an item as Control')
        return

    for channel in channels:
        channel_item = get_channel_item(channel)
        itemname_nospaces = recompile_nospaces(channel_item.id)
        name = f'{CONTROL_CHANNEL_PREFIX}{itemname_nospaces}_{get_channel_name(channel)}'
        username = f'{get_channel_item(channel).name} {get_channel_name(channel)}'
        mode = get_channel_mode(channel)
        ch_type = get_channel_type(channel)

        try:
            create_user_channel(control, name, username, mode, ch_type)
            from_channel: modo.Channel = control.channel(name)
            to_item: modo.Item = channel.item
            to_channel = to_item.channel(channel.name)
            link_channels(from_channel, to_channel)
        except RuntimeError:
            print(f'Error creating and linking channels for <{channel}> Possible dublication, skipped.')

    control.select(replace=True)


def  get_channel_selection() -> list[CHANNEL]:
    """ Get Channel Selection.
    lukpazera | Lukasz Pazera

    There is no utility class for handling channel selection
    like there is for items and scenes so it has to be done manually.
    """
    selection_service = lx.service.Selection()
    chan_sel_type = selection_service.LookupType(lx.symbol.sSELTYP_CHANNEL)

    # Channel selection is stored in packets, like all other selections.
    # Every packet contains information about one channel.
    # To read channel selection we have to use ChannelPacketTranslation object
    # that will decode selection packet and then we will be able to pull
    # channel information from it.
    # The line below initializes ChannelPacketTranslation object that is used to
    # extract selection information from selection packet.
    chan_transpacket = lx.object.ChannelPacketTranslation(selection_service.Allocate(lx.symbol.sSELTYP_CHANNEL))

    # To see how many elements of a given type are selected in scene
    # we use selection service's Count method.
    # We pass integer selection type code to the method,
    # in our case it's channel selection type code.
    chan_n = selection_service.Count(chan_sel_type)
    if not chan_n:
        return []

    # Now we're going to loop through all channel packets and read them by index.
    # To do that we're using selection service's ByIndex method passing it
    # channel selection code and an index of a packet we want to get.
    # The method returns a pointer to the packet. We're going to pass this pointer
    # to translaction packet to extract single channel selection.
    channels: list[CHANNEL] = []
    for x in range(chan_n):
        packet_pointer = selection_service.ByIndex(chan_sel_type, x)
        if not packet_pointer:
            lx.out('Bad selection packet, skipping...')
            continue

        # Channel selection is 2 elements:
        # item object the channel belongs to and a channel index.
        # To pull this information out from packet we use Item and Index methods
        # from ChannelPacketTranslation interface (that we already initialized) and
        # we pass packet pointer to these methods.
        item = lx.object.Item(chan_transpacket.Item(packet_pointer))
        chan_idx = chan_transpacket.Index(packet_pointer)

        # Show selection info in Event Log
        # lx.out('%s : %s' % (item.UniqueName(), item.ChannelName(chan_idx)))

        modo_item = modo.Item(item)
        if not modo_item:
            print(f'Failing to get modo item for lx item <{item.UniqueName()}>')
            continue

        channel_name = item.ChannelName(chan_idx)
        if not channel_name:
            print(f'Failing to get channel name for <{modo_item.name}> index <{chan_idx}>')
            continue

        channel = modo_item.channel(channel_name)
        if not channel:
            print(f'Failing to get channel for <{modo_item.name}> index <{chan_idx}> channel <{channel_name}>')
            continue

        channels.append(channel)

    return channels


def create_user_channel(control: modo.Item, name: str, username: str, mode: str, ch_type: str):
    if not mode:
        raise ValueError('Error getting channel mode.')
    if not ch_type:
        raise ValueError('Error getting channel type.')

    lx.eval(f'!channel.create {name} {ch_type} {mode} item:{control.id} username:{{{username}}}')


def get_channel_mode(channel: CHANNEL) -> str:
    VEC_XY = 'vecXY'
    VEC_XYZ = 'vecXYZ'
    VEC_RGB = 'vecRGB'
    VEC_RGBA = 'vecRGBA'
    VEC_UV = 'vecUV'
    VEC_UVW = 'vecUVW'

    if not isinstance(channel, modo.ChannelTriple):
        return 'scalar'

    channels: list[modo.Channel] = channel._channels
    for channel in channels:
        if channel.name.endswith('.X'):
            if len(channels) == 2:
                return VEC_XY
            return VEC_XYZ

        if channel.name.endswith('.R'):
            if len(channels) == 4:
                return VEC_RGBA
            return VEC_RGB

        if channel.name.endswith('.U'):
            if len(channels) == 2:
                return VEC_UV
            return VEC_UVW

    raise LookupError(f'Error getting ChannelTriple mode for channel <{channel}>.')


def get_channel_type(channel: CHANNEL) -> str:
    if not isinstance(channel, modo.ChannelTriple):
        return str(channel.storageType)

    channels: list[modo.Channel] = channel._channels
    if not channels:
        raise LookupError(f'Error getting ChannelTriple type for channel <{channel}>.')

    return str(channels[0].storageType)


def get_channel_name(channel: CHANNEL) -> str:
    if not isinstance(channel, modo.ChannelTriple):
        return channel.name

    channels: list[modo.Channel] = channel._channels
    if not channels:
        raise LookupError(f'Error getting ChannelTriple type for channel <{channel}>.')

    return channels[0].name[:-2]


def recompile_nospaces(name: str) -> str:
    regex = re.compile('[^a-zA-Z0-9]')

    return regex.sub('', name)


def get_channel_item(channel: CHANNEL) -> modo.Item:
    if not isinstance(channel, modo.ChannelTriple):
        return channel.item

    channels: list[modo.Channel] = channel._channels
    if not channels:
        raise LookupError(f'Error getting ChannelTriple type for channel <{channel}>.')

    return channels[0].item


def link_channels(ch_from: CHANNEL, ch_to: CHANNEL):
    if not isinstance(ch_from, modo.ChannelTriple) and not isinstance(ch_to, modo.ChannelTriple):
        lx.eval(f'channel.link add {{{ch_from.item.id}:{ch_from.name}}} {{{ch_to.item.id}:{ch_to.name}}}')
        return

    raise ValueError('Error linking channels: ChannelTriple detected.')


if __name__ == '__main__':
    main()

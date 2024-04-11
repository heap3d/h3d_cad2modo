#!/usr/bin/python
# ================================
# (C)2023-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# assign new material to unassigned ptags

import modo
import lx
from random import random

from h3d_utilites.scripts.h3d_utils import is_material_ptyp, replace_file_ext
from h3d_utilites.scripts.h3d_debug import H3dDebug


def get_mask_ptags(masks):
    ptags = set()
    for mask in masks:
        ptyp_channel = mask.channel('ptyp')
        if not ptyp_channel:
            continue
        ptyp = ptyp_channel.get()
        if not is_material_ptyp(ptyp):
            continue
        ptag_channel = mask.channel('ptag')
        if not ptag_channel:
            continue
        ptag = ptag_channel.get()
        ptags.add(ptag)

    return ptags


def get_geometry_ptags(meshes):
    ptags = set()
    for mesh in meshes:
        for poly in mesh.geometry.polygons:
            ptags.add(poly.materialTag)

    return ptags


def get_color_str(input_str):
    try:
        number_strings = input_str.strip().split()
        if len(number_strings) < 3:
            raise ValueError

        col_r = int(number_strings[-3]) / 255
        col_g = int(number_strings[-2]) / 255
        col_b = int(number_strings[-1]) / 255
        return '{} {} {}'.format(col_r, col_g, col_b)

    except ValueError:
        r, g, b = random(), random(), random()
        return '{} {} {}'.format(r, g, b)


def assign_new_material(geo_ptag, specific_color_str=None):
    if not geo_ptag:
        return
    meshes = modo.Scene().meshes
    if not meshes:
        return
    for mesh in meshes:
        if not mesh.geometry.polygons:
            continue
        for poly in mesh.geometry.polygons:
            if poly.materialTag != geo_ptag:
                continue
            mesh.select(replace=True)
            lx.eval('select.type polygon')
            poly.select(replace=True)
            if not specific_color_str:
                color_str = get_color_str(geo_ptag)
            else:
                color_str = specific_color_str
            lx.eval('poly.setMaterial "{}" {{{}}} {} {}'.format(geo_ptag, color_str, '0.8', '0.04'))
            # assign material for one polygon only, there is no need for do it for all polygons
            return


def assign_materials_to_unassigned_ptags(meshes, masks, use_color=False, color=None):
    masks_ptags = get_mask_ptags(masks)
    geometry_ptags = get_geometry_ptags(meshes)
    use_specific_color = use_color
    if use_specific_color:
        # specific_color = get_user_value(h3dc.USER_VAL_NAME_SPECIFIC_COLOR)
        specific_color = color
    else:
        specific_color = None

    for geo_ptag in geometry_ptags:
        if geo_ptag in masks_ptags:
            continue
        assign_new_material(geo_ptag, specific_color_str=specific_color)
        masks_ptags.add(geo_ptag)


log_name = replace_file_ext(modo.Scene().name)
h3dd = H3dDebug(enable=False, file=log_name)

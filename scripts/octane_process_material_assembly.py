#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# for processing octane material in preset
# load preset, clean all assemblies
# re-initiate octane override
# ================================

import modo
import modo.constants as c
import lx
import math
import os.path
import sys

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
import h3d_utils as h3du
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_cad2modo:}')))
import h3d_kit_constants as h3dc


def is_empty_assembly(item):
    print(item.type)
    if item.type != 'assembly':
        return False
    if item.itemGraph('itemGroups').forward():
        return False
    if item.itemGraph('parent').reverse():
        return False
    return True


def clear_group(item):
    # remove all items from assembly
    if not is_empty_assembly(item):
        item.select(replace=True)
        lx.eval('group.edit clr item')
    # call clear_group() for each assembly child
    if item.itemGraph('parent').reverse():
        for child in item.itemGraph('parent').reverse():
            clear_group(child)
    # remove empty assembly
    modo.scene.current().removeItems(item)


def process_assemblies(assemblies, opt):
    if not opt.OCTMAT_SETUP:
        return
    for asm in assemblies:
        print(asm.id)
        clear_group(asm)


def process_octane_overrides(opt):
    if not opt.OCTMAT_SETUP:
        return
    # get octane override material list
    octane_overrides = modo.scene.current().items(itype='material.octaneRenderer')
    for octane_override in octane_overrides:
        # edit in schematic for each octane override material
        modo.scene.current().deselect()
        lx.eval('!!select.subItem {} set'.format(octane_override.id))
        lx.eval('!!octane.materialMacro schematicEdit')


def process_render_settings(opt):
    if not opt.REND_SETUP:
        return
    # render settings setup
    modo.scene.current().renderItem.channel('resX').set(h3dc.RENDER_RESOLUTION)
    modo.scene.current().renderItem.channel('resY').set(h3dc.RENDER_RESOLUTION)
    modo.scene.current().renderItem.channel('aa').set(h3dc.RENDER_AA)
    modo.scene.current().renderItem.channel('reflSmps').set(h3dc.RENDER_SAMPLES)
    modo.scene.current().renderItem.channel('coarseRate').set(h3dc.RENDER_SHADER_RATE)
    # turn environment important sampling on
    modo.scene.current().renderItem.channel('envSample').set(1)
    # turn irradiance caching off
    modo.scene.current().renderItem.channel('irrCache').set(0)
    modo.scene.current().renderItem.channel('envRays').set(h3dc.RENDER_SAMPLES)
    shaders = modo.scene.current().items(itype='defaultShader')
    for shader in shaders:
        shader.channel('shadeRate').set(h3dc.RENDER_SHADER_RATE)


def process_lights(opt):
    if not opt.REND_SETUP:
        return
    if not opt.LIGHT_SETUP:
        return
    # turn all lights off
    for light in modo.scene.current().items(itype=c.LIGHT_TYPE):
        light.channel('visible').set('allOff')


def process_environment(opt):
    if not opt.REND_SETUP:
        return
    if not opt.ENV_SETUP:
        return
    # environment setup
    # check if env exist and delete old one
    envs = modo.scene.current().items(itype=c.ENVIRONMENT_TYPE)
    for env in envs:
        env.channel('visCam').set(0)
        for item in env.children():
            if item.type == 'imageMap':
                modo.scene.current().removeItems(item)
        lx.eval('texture.new "{}"'.format(opt.ENV_PATH))
        lx.eval('texture.parent {} 1'.format(env.id))
        lx.eval('item.channel (anyTxtrLocator)$projType spherical')
        lx.eval('item.channel (anyTxtrLocator)$projAxis y')
        lx.eval('transform.channel (anyTxtrLocator)$rot.Y {}'.format(opt.ENV_ROT_Y))
        lx.eval('texture.size 0 1.0')
        lx.eval('texture.size 1 1.0')
        lx.eval('texture.size 2 1.0')


def process_camera(camera, opt):
    if not opt.REND_SETUP:
        return
    if not opt.CAM_SETUP:
        return
    # camera setup
    camera.select(replace=True)
    lx.eval('transform.channel rot.X {}'.format(opt.CAM_ROT_X))
    lx.eval('transform.channel rot.Y {}'.format(opt.CAM_ROT_Y))
    lx.eval('transform.channel rot.Z {}'.format(0.0))
    modo.scene.current().deselect()
    for mesh in modo.scene.current().items(itype=c.MESH_TYPE):
        mesh.select()
    lx.eval('view3d.projection cam')
    lx.eval('camera.fit true true')
    lx.eval('viewport.fitSelected')


def save_as_preset_name(filename, opt):
    if not opt.SAVE_ENABLED:
        return
    # save the scene
    if filename != '':
        lx.eval('scene.saveAs "{}/{}.lxo" $LXOB false'.format(opt.STORE_DIR, filename))


class UiOptions:
    CAM_ROT_X = 0.0
    CAM_ROT_Y = 0.0
    ENV_ROT_Y = 0.0
    ENV_PATH = ""
    STORE_DIR = ""
    SAVE_ENABLED = False
    REND_SETUP = False
    OCTMAT_SETUP = False
    LIGHT_SETUP = False
    CAM_SETUP = False
    ENV_SETUP = False


def main():
    print('')
    print('octane_process_material_assembly.py start...')

    opt = UiOptions()
    # get user values from UI
    opt.CAM_ROT_X = math.degrees(h3du.get_user_value(h3dc.USER_VAL_CAM_ROT_X_NAME))
    opt.CAM_ROT_Y = math.degrees(h3du.get_user_value(h3dc.USER_VAL_CAM_ROT_Y_NAME))
    opt.ENV_ROT_Y = math.degrees(h3du.get_user_value(h3dc.USER_VAL_ENV_ROT_Y_NAME))
    opt.ENV_PATH = h3du.get_user_value(h3dc.USER_VAL_ENV_PATH_NAME)
    opt.STORE_DIR = h3du.get_user_value(h3dc.USER_VAL_STORE_DIR_NAME)
    opt.SAVE_ENABLED = h3du.get_user_value(h3dc.USER_VAL_SAVE_ENABLED_NAME)
    opt.REND_SETUP = h3du.get_user_value(h3dc.USER_VAL_REND_SETUP_NAME)
    opt.OCTMAT_SETUP = h3du.get_user_value(h3dc.USER_VAL_OCTMAT_SETUP_NAME)
    opt.LIGHT_SETUP = h3du.get_user_value(h3dc.USER_VAL_LIGHT_SETUP_NAME)
    opt.CAM_SETUP = h3du.get_user_value(h3dc.USER_VAL_CAM_SETUP_NAME)
    opt.ENV_SETUP = h3du.get_user_value(h3dc.USER_VAL_ENV_SETUP_NAME)

    # global SAVE_ENABLED
    # global REND_SETUP
    # check if environment image map exist
    if not os.path.exists(opt.ENV_PATH) and opt.ENV_SETUP:
        modo.dialogs.alert(
            title='Environment image map error',
            message='Environment image map <{}> doesn\'t exist, please set valid image map path'.format(opt.ENV_PATH),
            dtype='error'
        )
        exit()

    # check if store directory exist
    if not os.path.exists(opt.STORE_DIR) and opt.SAVE_ENABLED:
        modo.dialogs.alert(
            title='Directory error',
            message='Directory <{}> doesn\'t exist, please select valid store directory'.format(opt.STORE_DIR),
            dtype='error'
        )
        exit()

    if lx.args():
        for arg in lx.args():
            if arg == '-repair':
                opt.REND_SETUP = False
                opt.SAVE_ENABLED = False

    # get selected groups list
    groups = modo.scene.current().selectedByType(itype=c.GROUP_TYPE)
    # get root assemblies list
    root_assemblies = [item for item in groups if not item.itemGraph('parent').forward()]
    process_assemblies(root_assemblies, opt)

    process_octane_overrides(opt)

    process_render_settings(opt)

    process_lights(opt)

    process_environment(opt)

    # select camera 'Camera' or first one in the scene
    cameras = modo.scene.current().items(itype=c.CAMERA_TYPE, name='Camera')
    if not cameras:
        cameras = modo.scene.current().cameras
    if cameras:
        process_camera(cameras[0], opt)

    # get root material mask list
    root_masks = [mask for mask in modo.scene.current().items(itype=c.MASK_TYPE) if mask.parent.type == 'polyRender']
    # move root_mask children to root
    preset_name = ''
    for mask in root_masks:
        # skip if no .lxl in the name
        if '.lxl' not in mask.name:
            continue
        preset_name = mask.name[:-15]
        for mask_child in mask.children(recursive=False):
            if mask_child.type == 'mask':
                mask_child.setParent(modo.scene.current().renderItem, 1)
        # remove root_mask
        modo.scene.current().removeItems(mask)

    save_as_preset_name(preset_name, opt)

    print('octane_process_material_assembly.py done.')


if __name__ == '__main__':
    main()

#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# for processing octane material in preset
# load preset, clean all assemblies
# re initiate octane override
# ================================
import sys

import modo
import modo.constants as c
import lx
import math
import os.path

RENDER_RESOLUTION = 512
RENDER_AA = 's64'
RENDER_SAMPLES = 2048
RENDER_SHADER_RATE = 0.0
USER_VAL_CAM_ROT_X_NAME = 'h3d_opma_cam_rotX'
USER_VAL_CAM_ROT_Y_NAME = 'h3d_opma_cam_rotY'
USER_VAL_ENV_ROT_Y_NAME = 'h3d_opma_env_rotY'
USER_VAL_ENV_PATH_NAME = 'h3d_opma_env_path'
USER_VAL_STORE_DIR_NAME = 'h3d_opma_store_dir'
USER_VAL_SAVE_ENABLED_NAME = 'h3d_opma_save_enabled'
USER_VAL_REND_SETUP_NAME = 'h3d_opma_rend_setup'
USER_VAL_OCTMAT_SETUP_NAME = 'h3d_opma_octmat_setup'
USER_VAL_LIGHT_SETUP_NAME = 'h3d_opma_light_setup'
USER_VAL_CAM_SETUP_NAME = 'h3d_opma_cam_setup'
USER_VAL_ENV_SETUP_NAME = 'h3d_opma_env_setup'


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
    scene.removeItems(item)


def process_assemblies(assemblies):
    if not OCTMAT_SETUP:
        return
    for asm in assemblies:
        print(asm.id)
        clear_group(asm)


def process_octane_overrides():
    if not OCTMAT_SETUP:
        return
    # get octane override material list
    octane_overrides = scene.items(itype='material.octaneRenderer')
    for octane_override in octane_overrides:
        # edit in schematic for each octane override material
        scene.deselect()
        lx.eval('!!select.subItem {} set'.format(octane_override.id))
        lx.eval('!!octane.materialMacro schematicEdit')


def process_render_settings():
    if not REND_SETUP:
        return
    # render settings setup
    scene.renderItem.channel('resX').set(RENDER_RESOLUTION)
    scene.renderItem.channel('resY').set(RENDER_RESOLUTION)
    scene.renderItem.channel('aa').set(RENDER_AA)
    scene.renderItem.channel('reflSmps').set(RENDER_SAMPLES)
    scene.renderItem.channel('coarseRate').set(RENDER_SHADER_RATE)
    # turn environment important sampling on
    scene.renderItem.channel('envSample').set(1)
    # turn irradiance caching off
    scene.renderItem.channel('irrCache').set(0)
    scene.renderItem.channel('envRays').set(RENDER_SAMPLES)
    shaders = scene.items(itype='defaultShader')
    for shader in shaders:
        shader.channel('shadeRate').set(RENDER_SHADER_RATE)


def process_lights():
    if not REND_SETUP:
        return
    if not LIGHT_SETUP:
        return
    # turn all lights off
    for light in scene.items(itype=c.LIGHT_TYPE):
        light.channel('visible').set('allOff')


def process_environment():
    if not REND_SETUP:
        return
    if not ENV_SETUP:
        return
    # environment setup
    # check if env exist and delete old one
    envs = scene.items(itype=c.ENVIRONMENT_TYPE)
    for env in envs:
        env.channel('visCam').set(0)
        for item in env.children():
            if item.type == 'imageMap':
                scene.removeItems(item)
        lx.eval('texture.new "{}"'.format(ENV_PATH))
        lx.eval('texture.parent {} 1'.format(env.id))
        lx.eval('item.channel (anyTxtrLocator)$projType spherical')
        lx.eval('item.channel (anyTxtrLocator)$projAxis y')
        lx.eval('transform.channel (anyTxtrLocator)$rot.Y {}'.format(ENV_ROT_Y))
        lx.eval('texture.size 0 1.0')
        lx.eval('texture.size 1 1.0')
        lx.eval('texture.size 2 1.0')


def process_camera(camera):
    if not REND_SETUP:
        return
    if not CAM_SETUP:
        return
    # camera setup
    camera.select(replace=True)
    lx.eval('transform.channel rot.X {}'.format(CAM_ROT_X))
    lx.eval('transform.channel rot.Y {}'.format(CAM_ROT_Y))
    lx.eval('transform.channel rot.Z {}'.format(0.0))
    scene.deselect()
    for mesh in scene.items(itype=c.MESH_TYPE):
        mesh.select()
    lx.eval('view3d.projection cam')
    lx.eval('camera.fit true true')
    lx.eval('viewport.fitSelected')


def save_as_preset_name(filename):
    if not SAVE_ENABLED:
        return
    # save the scene
    if filename != '':
        lx.eval('scene.saveAs "{}/{}.lxo" $LXOB false'.format(STORE_DIR, filename))


if __name__ == '__main__':
    # get user values from UI
    CAM_ROT_X = math.degrees(lx.eval('user.value {} ?'.format(USER_VAL_CAM_ROT_X_NAME)))
    CAM_ROT_Y = math.degrees(lx.eval('user.value {} ?'.format(USER_VAL_CAM_ROT_Y_NAME)))
    ENV_ROT_Y = math.degrees(lx.eval('user.value {} ?'.format(USER_VAL_ENV_ROT_Y_NAME)))
    ENV_PATH = lx.eval('user.value {} ?'.format(USER_VAL_ENV_PATH_NAME))
    STORE_DIR = lx.eval('user.value {} ?'.format(USER_VAL_STORE_DIR_NAME))
    SAVE_ENABLED = lx.eval('user.value {} ?'.format(USER_VAL_SAVE_ENABLED_NAME))
    REND_SETUP = lx.eval('user.value {} ?'.format(USER_VAL_REND_SETUP_NAME))
    OCTMAT_SETUP = lx.eval('user.value {} ?'.format(USER_VAL_OCTMAT_SETUP_NAME))
    LIGHT_SETUP = lx.eval('user.value {} ?'.format(USER_VAL_LIGHT_SETUP_NAME))
    CAM_SETUP = lx.eval('user.value {} ?'.format(USER_VAL_CAM_SETUP_NAME))
    ENV_SETUP = lx.eval('user.value {} ?'.format(USER_VAL_ENV_SETUP_NAME))

    scene = modo.scene.current()
    # check if environment image map exist
    if not os.path.exists(ENV_PATH) and ENV_SETUP:
        modo.dialogs.alert(
            title='Environment image map error',
            message='Environment image map <{}> doesn\'t exist, please set valid image map path'.format(ENV_PATH),
            dtype='error'
        )
        exit()

    # check if store directory exist
    if not os.path.exists(STORE_DIR) and SAVE_ENABLED:
        modo.dialogs.alert(
            title='Directory error',
            message='Directory <{}> doesn\'t exist, please select valid store directory'.format(STORE_DIR),
            dtype='error'
        )
        exit()

    if lx.args():
        for arg in lx.args():
            if arg == '-repair':
                REND_SETUP = False
                SAVE_ENABLED = False

    # get selected groups list
    groups = scene.selectedByType(itype=c.GROUP_TYPE)
    # get root assemblies list
    root_assemblies = [item for item in groups if not item.itemGraph('parent').forward()]
    process_assemblies(root_assemblies)

    process_octane_overrides()

    process_render_settings()

    process_lights()

    process_environment()

    # select camera 'Camera' or first one in the scene
    cameras = scene.items(itype=c.CAMERA_TYPE, name='Camera')
    if not cameras:
        cameras = scene.cameras
    if cameras:
        process_camera(cameras[0])

    # get root material mask list
    root_masks = [mask for mask in scene.items(itype=c.MASK_TYPE) if mask.parent.type == 'polyRender']
    # move root_mask children to root
    preset_name = ''
    for mask in root_masks:
        # skip if no .lxl in the name
        if '.lxl' not in mask.name:
            continue
        preset_name = mask.name[:-15]
        for mask_child in mask.children(recursive=False):
            if mask_child.type == 'mask':
                mask_child.setParent(scene.renderItem, 1)
        # remove root_mask
        scene.removeItems(mask)

    save_as_preset_name(preset_name)

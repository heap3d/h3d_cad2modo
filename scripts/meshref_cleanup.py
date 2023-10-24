#!/usr/bin/python
# ================================
# (C)2022-2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# cleanup meshref scene file

from typing import Iterable
import lx
import modo
import modo.constants as c
import sys

sys.path.append(
    "{}\\scripts".format(lx.eval("query platformservice alias ? {kit_h3d_utilites:}"))
)
import h3d_utils as h3du
from h3d_debug import H3dDebug

sys.path.append(
    "{}\\scripts".format(lx.eval("query platformservice alias ? {kit_h3d_cad2modo:}"))
)
import remove_duplicated_scene_items

USERVAL_NAME_CMR_DEL_MESH_INSTANCE = "h3d_cmr_del_mesh_instance"
USERVAL_NAME_CMR_MESH_INSTANCE_TO_MESH = "h3d_cmr_mesh_instance_to_mesh"
USERVAL_NAME_CMR_MESH_INSTANCE_TO_LOC = "h3d_cmr_mesh_instance_to_loc"
USERVAL_NAME_CMR_MESH_LOC_SIZE = "h3d_cmr_mesh_loc_size"
USERVAL_NAME_CMR_DEL_VOID_MESH = "h3d_cmr_del_void_mesh"
USERVAL_NAME_CMR_DEL_LOC = "h3d_cmr_del_loc"
USERVAL_NAME_CMR_DEL_GRP_LOC = "h3d_cmr_del_grp_loc"
USERVAL_NAME_CMR_DEL_ASSEMBLY = "h3d_cmr_del_assembly"
USERVAL_NAME_CMR_DEL_GROUP = "h3d_cmr_del_group"
USERVAL_NAME_CMR_DEL_POLYGON_PART_TAG = "h3d_cmr_del_polygon_part"
USERVAL_NAME_CMR_FLATTEN_SCENE = "h3d_cmr_flatten_scene"
USERVAL_NAME_CMR_DEL_ENVIRONMENT = "h3d_cmr_del_environments"
USERVAL_NAME_CMR_DEL_MATERIAL = "h3d_cmr_del_materials"


class UserOptions:
    del_mesh_instance = False
    mesh_instance_to_mesh = False
    mesh_instance_to_loc = False
    loc_size = 0.0
    del_void_mesh = False
    del_loc = False
    del_grp_loc = False
    del_assembly = False
    del_group = False
    del_polygon_part = False
    flatten_scene = False
    del_environments = False
    del_materials = False


def is_protected_item(item, types, options):
    """returns True if item is protected. Otherwise returns False"""
    protected = False
    if h3du.safe_type(item) in types:
        protected = True
    if options.del_void_mesh:
        if h3du.itype_str(c.MESH_TYPE) in types:
            # process void mesh items
            if is_void_mesh(item):
                # mesh item is not protected if no polygons
                protected = False

    return protected


def is_protected_children(item, types, options):
    """returns True if any of the children is protected. Otherwise returns False"""
    if any(is_protected_item(x, types, options) for x in item.children(recursive=True)):
        return True

    return False


def is_protected(item, types, options):
    """returns True if item is protected type or any of children is protected"""
    if is_protected_item(item, types, options):
        return True
    if is_protected_children(item, types, options):
        return True

    return False


def is_void_mesh(mesh):
    """returns True if item is mesh with no polygons. Otherwise returns False. If item is not a mesh returns None"""
    if not mesh:
        return None
    if mesh.type != h3du.itype_str(c.MESH_TYPE):
        return None
    if mesh.geometry.polygons:
        return False

    return True


def get_static_protected():
    """get list of options independent protected items"""
    static_protected = set()
    # Scene item
    static_protected.add(modo.Scene().sceneItem)
    # Render item
    static_protected.add(modo.Scene().renderItem)
    # Bake items
    bake_items = modo.Scene().items(itype=c.SHADERFOLDER_TYPE, name="Bake Items*")
    static_protected.update(bake_items[:1])
    # Nodes
    nodes = modo.Scene().items(itype=c.SHADERFOLDER_TYPE, name="Nodes*")
    static_protected.update(nodes[:1])
    # Environments
    environments = modo.Scene().items(itype=c.SHADERFOLDER_TYPE, name="Environments*")
    static_protected.update(environments[:1])
    # Library
    librarys = modo.Scene().items(itype=c.SHADERFOLDER_TYPE, name="Library*")
    static_protected.update(librarys[:1])
    # Lights
    lights = modo.Scene().items(itype=c.SHADERFOLDER_TYPE, name="Lights*")
    static_protected.update(lights[:1])
    # Schematic nodes
    schematicNodes = modo.Scene().items(itype=c.SCHMNODE_TYPE)
    static_protected.update(schematicNodes)
    # Base material
    root_mats = [
        i
        for i in modo.Scene().items(itype=c.ADVANCEDMATERIAL_TYPE)
        if (i.parent is None or i.parent.type == h3du.itype_str(c.POLYRENDER_TYPE))
    ]
    h3dd.print_items(root_mats, "roots mats:")
    static_protected.update(root_mats[:1])
    # Transforms
    transforms = set(
        i for i in modo.Scene().items(itype=c.TRANSFORM_TYPE, superType=True)
    )
    static_protected.update(transforms)

    return static_protected


def get_connected(item: modo.Item):
    """get connected items"""
    return item.itemGraph("shadeLoc").connectedItems["Forward"]


def get_environment_collection(item: modo.Item):
    """get environment's children and connected items"""
    env_collection = item.children(recursive=True)
    for child in env_collection:
        env_collection.extend(get_connected(child))

    return env_collection


def get_protected(items: Iterable[modo.Item], types, options: UserOptions):
    """gets list of items with a specific types according to options"""
    # collect Protected items
    filtered = set()
    filtered.update(get_static_protected())

    for item in items:
        if item in filtered:
            continue
        if not is_protected(item, types, options):
            continue
        # add item to filtered set
        filtered.add(item)
        # add protected item's parents
        if item.parents:
            filtered.update(item.parents)
        # add environment children
        isEnvironment = item.type == h3du.itype_str(c.ENVIRONMENT_TYPE)
        if isEnvironment and not options.del_environments:
            filtered.update(get_environment_collection(item))

    return filtered


def clear_assemblies(assemblies):
    for assembly in assemblies:
        # check if any items in the assembly
        if not assembly.itemGraph("itemGroups").forward():
            continue
        assembly.select(replace=True)
        lx.eval("group.edit clr all")


def get_root_assemblies(assemblies):
    return set(i for i in assemblies if not i.parent)


def delete_item(item):
    h3dd.print_debug(
        "removing <{}> {} {} ...".format(
            h3dd.get_name(item), item, h3du.safe_type(item)
        ),
        indent=1,
    )
    try:
        item.select(replace=True)
    except LookupError:
        h3dd.print_debug("item not found!", indent=2)
        return
    modo.Scene().removeItems(item)


def remove_items_from_scene(items):
    # process assemblies
    assemblies = set(i for i in items if i.type == "assembly")
    clear_assemblies(assemblies)
    root_assemblies = get_root_assemblies(assemblies)
    h3dd.print_debug("Remove assemblies:")
    for root_assembly in root_assemblies:
        delete_item(root_assembly)
    h3dd.print_debug("done.")
    items = items - assemblies

    # process groups
    groups = set(i for i in items if h3du.safe_type(i) == "group")
    h3dd.print_debug("Remove groups:")
    for group in groups:
        delete_item(group)
    h3dd.print_debug("done.")
    items = items - groups

    # remove all environments
    environments = set(i for i in items if i.type == h3du.itype_str(c.ENVIRONMENT_TYPE))
    duplicates = set()
    if len(environments) == 1:
        for env in environments:
            duplicates.add(modo.Scene().duplicateItem(env))
    environments.update(duplicates)
    h3dd.print_debug("Remove environments:")
    for environment in environments:
        delete_item(environment)
    h3dd.print_debug("done.")
    items = items - environments

    # octane material overrides
    octane_mats = set(modo.Scene().items(itype="material.octaneRenderer"))
    h3dd.print_debug("Remove octane materials:")
    for octane_mat in octane_mats:
        delete_item(octane_mat)
    h3dd.print_debug("done.")
    items = items - octane_mats

    # delete rest of the items
    h3dd.print_debug("Remove other items:")
    for item in items:
        delete_item(item)
    h3dd.print_debug("done.")


def add_base_material():
    h3dd.print_debug("adding base material:")
    h3dd.print_debug("creating advancedMaterial...", 1)
    modo.Scene().renderItem.select()
    lx.eval("shader.create advancedMaterial")
    h3dd.print_debug("enabling smooth area weight...", 1)
    modo.Scene().renderItem.select()
    lx.eval("material.smoothAreaWeight area")
    h3dd.print_debug("enabling smooth weight angle...", 1)
    modo.Scene().renderItem.select()
    lx.eval("material.smoothWeight angle true")
    h3dd.print_debug("done.")


def set_polygon_part(mesh, part_tag="Default"):
    mesh.select(replace=True)
    lx.eval('poly.setPart "{}"'.format(part_tag))


def flatten_scene_hierarchy():
    for item in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True):
        if not item.parent:
            continue
        item.select(replace=True)
        lx.eval("item.parent parent:{} inPlace:1")


def mesh_instance_to_mesh(meshinst):
    meshinst.select(replace=True)
    h3dd.print_debug("<{}>    {}    {}".format(meshinst.name, meshinst, meshinst.type))
    name = meshinst.name
    lx.eval("item.setType mesh locator")
    lx.eval("item.name {{{}}} locator".format(name))
    return modo.Scene().selectedByType(itype=c.MESH_TYPE)[0]


def mesh_instance_to_loc(meshinst):
    h3dd.print_debug("<{}>    {}    {}".format(meshinst.name, meshinst, meshinst.type))
    meshinst.select(replace=True)
    name = meshinst.name
    lx.eval("item.setType locator locator")
    lx.eval("item.name {{{}}} locator".format(name))
    return modo.Scene().selectedByType(itype=c.LOCATOR_TYPE)[0]


def main():
    print("")
    print("meshref_cleanup.py start...")

    filter_types = {h3du.itype_str(c.MESH_TYPE), h3du.itype_str(c.MORPHDEFORM_TYPE)}

    opt = UserOptions()

    opt.del_mesh_instance = h3du.get_user_value(USERVAL_NAME_CMR_DEL_MESH_INSTANCE)
    opt.mesh_instance_to_mesh = h3du.get_user_value(
        USERVAL_NAME_CMR_MESH_INSTANCE_TO_MESH
    )
    opt.mesh_instance_to_loc = h3du.get_user_value(
        USERVAL_NAME_CMR_MESH_INSTANCE_TO_LOC
    )
    opt.del_void_mesh = h3du.get_user_value(USERVAL_NAME_CMR_DEL_VOID_MESH)
    opt.del_loc = h3du.get_user_value(USERVAL_NAME_CMR_DEL_LOC)
    opt.del_grp_loc = h3du.get_user_value(USERVAL_NAME_CMR_DEL_GRP_LOC)
    opt.del_assembly = h3du.get_user_value(USERVAL_NAME_CMR_DEL_ASSEMBLY)
    opt.del_group = h3du.get_user_value(USERVAL_NAME_CMR_DEL_GROUP)
    opt.del_polygon_part = h3du.get_user_value(USERVAL_NAME_CMR_DEL_POLYGON_PART_TAG)
    opt.flatten_scene = h3du.get_user_value(USERVAL_NAME_CMR_FLATTEN_SCENE)
    opt.loc_size = h3du.get_user_value(USERVAL_NAME_CMR_MESH_LOC_SIZE)
    opt.del_environments = h3du.get_user_value(USERVAL_NAME_CMR_DEL_ENVIRONMENT)
    opt.del_materials = h3du.get_user_value(USERVAL_NAME_CMR_DEL_MATERIAL)

    # update safe types according to user options
    if not opt.del_mesh_instance:
        filter_types.add(h3du.itype_str(c.MESHINST_TYPE))
    if opt.mesh_instance_to_mesh:
        filter_types.add(h3du.itype_str(c.MESHINST_TYPE))
    if not opt.del_loc:
        filter_types.add(h3du.itype_str(c.LOCATOR_TYPE))
    if not opt.del_grp_loc:
        filter_types.add(h3du.itype_str(c.GROUPLOCATOR_TYPE))
    if not opt.del_assembly:
        filter_types.add("assembly")
    if not opt.del_group:
        filter_types.add(h3du.itype_str(c.GROUP_TYPE))
    if not opt.del_environments:
        filter_types.add(h3du.itype_str(c.ENVIRONMENT_TYPE))
    if not opt.del_materials:
        filter_types.add(h3du.itype_str(c.MASK_TYPE))
        filter_types.add(h3du.itype_str(c.ADVANCEDMATERIAL_TYPE))
        filter_types.add(h3du.itype_str(c.DEFAULTSHADER_TYPE))

    # flatten scene hierarchy
    if opt.flatten_scene:
        flatten_scene_hierarchy()

    scene_items = set(modo.scene.current().items())
    protected_items = get_protected(scene_items, filter_types, opt)
    items_to_delete = scene_items - protected_items

    h3dd.print_items(filter_types, "Filter types:")
    h3dd.print_items(protected_items, "Protected items:")

    remove_items_from_scene(items_to_delete)

    if not modo.Scene().items(itype=c.ADVANCEDMATERIAL_TYPE):
        add_base_material()
    else:
        h3dd.print_items(
            modo.Scene().items(itype=c.ADVANCEDMATERIAL_TYPE), "advanced materials:"
        )

    # process polygon parts
    if opt.del_polygon_part:
        for mesh in modo.Scene().items(itype=c.MESH_TYPE):
            set_polygon_part(mesh)

    selection_store = set()

    # convert mesh instances to meshes
    if opt.mesh_instance_to_mesh:
        instances = modo.Scene().items(itype=c.MESHINST_TYPE)
        for meshinst in instances:
            selection_store.add(mesh_instance_to_mesh(meshinst))

    # convert mesh instances to locators
    if opt.mesh_instance_to_loc:
        instances = modo.Scene().items(itype=c.MESHINST_TYPE)
        for meshinst in instances:
            loc = mesh_instance_to_loc(meshinst)
            selection_store.add(loc)
            loc.select(replace=True)
            lx.eval("item.channel locator$size {}".format(opt.loc_size))

    # delete mesh instances
    if opt.del_mesh_instance:
        instances = modo.Scene().items(itype=c.MESHINST_TYPE)
        for meshinst in instances:
            delete_item(meshinst)

    # remove duplicated FX items
    remove_duplicated_scene_items.main()

    # select modified instances
    modo.Scene().deselect()
    for item in selection_store:
        item.select()

    print("meshref_cleanup.py done.")


if __name__ == "__main__":
    h3dd = H3dDebug(
        enable=True, file=h3du.replace_file_ext(modo.Scene().filename, ".log")
    )
    main()

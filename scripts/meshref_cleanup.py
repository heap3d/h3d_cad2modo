#!/usr/bin/python
# ================================
# (C)2022-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# cleanup meshref scene file

from typing import Iterable
import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import safe_type, itype_str, get_user_value

import h3d_cad2modo.scripts.remove_duplicated_scene_items as remove_duplicated_scene_items

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
USERVAL_NAME_CMR_DEL_SCHEMATIC_NODES = "h3d_cmr_del_schematic_nodes"


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
    del_schematic_nodes = False


def main():
    filter_types = {itype_str(c.MESH_TYPE), itype_str(c.MORPHDEFORM_TYPE)}

    opt = UserOptions()

    opt.del_mesh_instance = get_user_value(USERVAL_NAME_CMR_DEL_MESH_INSTANCE)
    opt.mesh_instance_to_mesh = get_user_value(USERVAL_NAME_CMR_MESH_INSTANCE_TO_MESH)
    opt.mesh_instance_to_loc = get_user_value(USERVAL_NAME_CMR_MESH_INSTANCE_TO_LOC)
    opt.del_void_mesh = get_user_value(USERVAL_NAME_CMR_DEL_VOID_MESH)
    opt.del_loc = get_user_value(USERVAL_NAME_CMR_DEL_LOC)
    opt.del_grp_loc = get_user_value(USERVAL_NAME_CMR_DEL_GRP_LOC)
    opt.del_assembly = get_user_value(USERVAL_NAME_CMR_DEL_ASSEMBLY)
    opt.del_group = get_user_value(USERVAL_NAME_CMR_DEL_GROUP)
    opt.del_polygon_part = get_user_value(USERVAL_NAME_CMR_DEL_POLYGON_PART_TAG)
    opt.flatten_scene = get_user_value(USERVAL_NAME_CMR_FLATTEN_SCENE)
    opt.loc_size = get_user_value(USERVAL_NAME_CMR_MESH_LOC_SIZE)
    opt.del_environments = get_user_value(USERVAL_NAME_CMR_DEL_ENVIRONMENT)
    opt.del_materials = get_user_value(USERVAL_NAME_CMR_DEL_MATERIAL)
    opt.del_schematic_nodes = get_user_value(USERVAL_NAME_CMR_DEL_SCHEMATIC_NODES)

    # update safe types according to user options
    if not opt.del_mesh_instance:
        filter_types.add(itype_str(c.MESHINST_TYPE))
    if opt.mesh_instance_to_mesh:
        filter_types.add(itype_str(c.MESHINST_TYPE))
    if not opt.del_loc:
        filter_types.add(itype_str(c.LOCATOR_TYPE))
    if not opt.del_grp_loc:
        filter_types.add(itype_str(c.GROUPLOCATOR_TYPE))
    if not opt.del_assembly:
        filter_types.add("assembly")
    if not opt.del_group:
        filter_types.add(itype_str(c.GROUP_TYPE))
    if not opt.del_environments:
        filter_types.add(itype_str(c.ENVIRONMENT_TYPE))
    if not opt.del_materials:
        filter_types.add(itype_str(c.MASK_TYPE))
        filter_types.add(itype_str(c.ADVANCEDMATERIAL_TYPE))
        filter_types.add(itype_str(c.DEFAULTSHADER_TYPE))
    if not opt.del_schematic_nodes:
        filter_types.add(itype_str(c.SCHMNODE_TYPE))

    # flatten scene hierarchy
    if opt.flatten_scene:
        flatten_scene_hierarchy()

    scene_items = set(scene.items())
    protected_items = get_protected(scene_items, filter_types, opt)
    protected_connected_items = get_protected_connected_items(protected_items)
    items_to_delete = scene_items - protected_items - protected_connected_items

    remove_items_from_scene(items_to_delete)

    if not scene.items(itype=c.ADVANCEDMATERIAL_TYPE):
        add_base_material()
    # process polygon parts
    if opt.del_polygon_part:
        for mesh in scene.items(itype=c.MESH_TYPE):
            set_polygon_part(mesh)

    selection_store = set()

    # convert mesh instances to meshes
    if opt.mesh_instance_to_mesh:
        instances = scene.items(itype=c.MESHINST_TYPE)
        for meshinst in instances:
            selection_store.add(mesh_instance_to_mesh(meshinst))

    # convert mesh instances to locators
    if opt.mesh_instance_to_loc:
        instances = scene.items(itype=c.MESHINST_TYPE)
        for meshinst in instances:
            loc = mesh_instance_to_loc(meshinst)
            selection_store.add(loc)
            loc.select(replace=True)
            lx.eval("item.channel locator$size {}".format(opt.loc_size))

    # delete mesh instances
    if opt.del_mesh_instance:
        instances = scene.items(itype=c.MESHINST_TYPE)
        for meshinst in instances:
            delete_item(meshinst)

    # remove duplicated FX items
    remove_duplicated_scene_items.main()

    # select modified instances
    scene.deselect()
    for item in selection_store:
        item.select()


def is_protected_item(item, types, options):
    """returns True if item is protected. Otherwise returns False"""
    protected = False
    if safe_type(item) in types:
        protected = True
    if options.del_void_mesh:
        if itype_str(c.MESH_TYPE) in types:
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
    if mesh.type != itype_str(c.MESH_TYPE):
        return None
    if mesh.geometry.polygons:
        return False

    return True


def get_static_protected():
    """get list of options independent protected items"""
    static_protected = set()
    # Scene item
    static_protected.add(scene.sceneItem)
    # Render item
    static_protected.add(scene.renderItem)
    # Bake items
    bake_items = scene.items(itype=c.SHADERFOLDER_TYPE, name="Bake Items*")
    static_protected.update(bake_items[:1])
    # Nodes
    nodes = scene.items(itype=c.SHADERFOLDER_TYPE, name="Nodes*")
    static_protected.update(nodes[:1])
    # Environments
    environments = scene.items(itype=c.SHADERFOLDER_TYPE, name="Environments*")
    static_protected.update(environments[:1])
    # Library
    librarys = scene.items(itype=c.SHADERFOLDER_TYPE, name="Library*")
    static_protected.update(librarys[:1])
    # Lights
    lights = scene.items(itype=c.SHADERFOLDER_TYPE, name="Lights*")
    static_protected.update(lights[:1])
    # Base material
    root_mats = [
        i
        for i in scene.items(itype=c.ADVANCEDMATERIAL_TYPE)
        if (i.parent is None or i.parent.type == itype_str(c.POLYRENDER_TYPE))
    ]
    static_protected.update(root_mats[:1])
    # Transforms
    transforms = set(
        i for i in scene.items(itype=c.TRANSFORM_TYPE, superType=True)
    )
    static_protected.update(transforms)

    return static_protected


def get_connected_shader_items(item: modo.Item) -> list[modo.Item]:
    """get connected items from item graph shadeLoc for specified item

    Args:
        item (modo.Item): item to get connections

    Returns:
        list[modo.Item]: list of connected items
    """
    return item.itemGraph("shadeLoc").connectedItems["Forward"]  # type: ignore


def get_environment_collection(item: modo.Item) -> list[modo.Item]:
    """get environment's children and connected items

    Args:
        item (modo.Item): item to get collection

    Returns:
        list[modo.Item]: list of children and connected items
    """
    env_collection = item.children(recursive=True)
    for child in env_collection:
        env_collection.extend(get_connected_shader_items(child))  # type: ignore

    return env_collection


def get_protected(items: Iterable[modo.Item], types: set[str], options: UserOptions) -> set[modo.Item]:
    """gets list of items prohibited to remove from the scene

    Args:
        items (Iterable[modo.Item]): list of items to filter
        types (set[str]): set of types to filter
        options (UserOptions): user options to filter

    Returns:
        set[modo.Item]: set of filtered items ptohibited to remove from the scene
    """
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
        isEnvironment = item.type == itype_str(c.ENVIRONMENT_TYPE)
        if isEnvironment and not options.del_environments:
            filtered.update(get_environment_collection(item))

    return filtered


def clear_assemblies(assemblies: Iterable[modo.Item]) -> None:
    for assembly in assemblies:
        # check if any items in the assembly
        if not assembly.itemGraph("itemGroups").forward():
            continue
        assembly.select(replace=True)
        lx.eval("group.edit clr all")


def get_root_assemblies(assemblies) -> set[modo.Item]:
    return set(i for i in assemblies if not i.parent)


def delete_item(item):
    try:
        item.select(replace=True)
    except LookupError:
        return
    scene.removeItems(item)


def remove_items_from_scene(items):
    # process assemblies
    assemblies = set(i for i in items if i.type == "assembly")
    clear_assemblies(assemblies)
    root_assemblies = get_root_assemblies(assemblies)
    for root_assembly in root_assemblies:
        delete_item(root_assembly)
    items = items - assemblies

    # process groups
    groups = set(i for i in items if safe_type(i) == "group")
    for group in groups:
        delete_item(group)
    items = items - groups

    # remove all environments
    environments = set(i for i in items if i.type == itype_str(c.ENVIRONMENT_TYPE))
    duplicates = set()
    if len(environments) == 1:
        for env in environments:
            duplicates.add(scene.duplicateItem(env))
    environments.update(duplicates)
    for environment in environments:
        delete_item(environment)
    items = items - environments

    # octane material overrides
    try:
        octane_mats = set(scene.items(itype="material.octaneRenderer"))
        for octane_mat in octane_mats:
            delete_item(octane_mat)
        items = items - octane_mats
    except LookupError:
        print('Octane Overrides not found.')

    # delete rest of the items
    for item in items:
        delete_item(item)


def add_base_material():
    scene.renderItem.select()
    lx.eval("shader.create advancedMaterial")
    scene.renderItem.select()
    lx.eval("material.smoothAreaWeight area")
    scene.renderItem.select()
    lx.eval("material.smoothWeight angle true")


def set_polygon_part(mesh: modo.Item, part_tag: str = "Default"):
    mesh.select(replace=True)
    lx.eval('!poly.setPart "{}"'.format(part_tag))


def flatten_scene_hierarchy():
    for item in scene.items(itype=c.LOCATOR_TYPE, superType=True):
        if not item.parent:
            continue
        item.select(replace=True)
        lx.eval("item.parent parent:{} inPlace:1")


def mesh_instance_to_mesh(meshinst):
    meshinst.select(replace=True)
    name = meshinst.name
    lx.eval("item.setType mesh locator")
    lx.eval("item.name {{{}}} locator".format(name))
    return scene.selectedByType(itype=c.MESH_TYPE)[0]


def mesh_instance_to_loc(meshinst):
    meshinst.select(replace=True)
    name = meshinst.name
    lx.eval("item.setType locator locator")
    lx.eval("item.name {{{}}} locator".format(name))
    return scene.selectedByType(itype=c.LOCATOR_TYPE)[0]


def get_connected_items_to_protect(item: modo.Item, known_items: set[modo.Item]) -> set[modo.Item]:
    if not item:
        return set()
    if item.superType == 'transform':
        return set()
    if item in known_items:
        return set()
    if item.type == itype_str(c.SCENE_TYPE):
        return set()
    if item.type == itype_str(c.ENVIRONMENT_TYPE):
        return set()
    if item.type == itype_str(c.SHADERFOLDER_TYPE):
        return set()
    if item.type == itype_str(c.POLYRENDER_TYPE):
        return set()

    connections: set[modo.Item] = set()
    for graph in item.itemGraphs:
        if graph.type == 'itemGroups':
            continue
        if graph.type == 'schmNode':
            continue
        if graph.type == 'xfrmCore':
            continue
        if graph.type == 'scene':
            continue
        forward_connections = graph.forward()
        reverse_connections = graph.reverse()
        if forward_connections:
            connections = connections.union(forward_connections)  # type: ignore
        if reverse_connections:
            connections = connections.union(reverse_connections)  # type: ignore

        known_items.add(item)

    for recursive_item in connections:
        connections = connections.union(get_connected_items_to_protect(recursive_item, known_items))

    return connections


def get_protected_connected_items(items: set[modo.Item]) -> set[modo.Item]:

    if not items:
        return set()
    protected_connected_items: set[modo.Item] = set()
    for item in items:
        connected_items_to_protect = get_connected_items_to_protect(item, protected_connected_items)
        protected_connected_items = protected_connected_items.union(connected_items_to_protect)

    return protected_connected_items


if __name__ == "__main__":
    print("")
    print("meshref_cleanup.py start...")

    scene = modo.Scene()
    main()

    print("meshref_cleanup.py done.")

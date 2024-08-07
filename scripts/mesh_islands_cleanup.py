#!/usr/bin/python
# ================================
# (C)2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# mesh cleanup by mesh islands
# select mesh items and run the script

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import replace_file_ext, get_user_value
from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_exceptions import H3dExitException


REMOVE_FLOATING_VERTICES = "h3d_imc_remove_floating_vertices"
REMOVE_ONE_POINT_POLYGONS = "h3d_imc_remove_one_point_polygons"
REMOVE_TWO_POINTS_POLYGONS = "h3d_imc_remove_two_points_polygons"
FIX_DUPLICATE_POINTS_IN_POLYGON = "h3d_imc_fix_duplicate_points_in_polygon"
REMOVE_COLINEAR_VERTICES = "h3d_imc_remove_colinear_vertices"
FIX_FACE_NORMAL_VECTORS = "h3d_imc_fix_face_normal_vectors"
MERGE_VERTICES = "h3d_imc_merge_vertices"
MERGE_DISCO_VALUES = "h3d_imc_merge_disco_values"
UNIFY_POLYGONS = "h3d_imc_unify_polygons"
FORCE_UNIFY = "h3d_imc_force_unify"
REMOVE_DISCO_WEIGHT_VALUES = "h3d_imc_remove_disco_weight_values"
LAST_STEP_MERGE_VERTICES = "h3d_imc_merge_vertices_last_step"
FIX_GAPS = "h3d_imc_fix_gaps"
NOFINAL = 'nofinal'


class Options:
    remove_floating_vertices = False
    remove_one_point_polygons = False
    remove_two_points_polygons = False
    fix_duplicate_points_in_polygon = False
    remove_colinear_vertices = False
    fix_face_normal_vectors = False
    merge_vertices = False
    merge_disco_values = False
    unify_polygons = False
    force_unify = False
    remove_disco_weight_values = False
    fix_gaps = False
    last_step_merge_vertices = False
    final_mesh_cleanup = True


def mesh_cleanup_versions(opt: Options, last_step: bool = False) -> None:
    if lx.service.Platform().AppVersion() < 1700:  # type: ignore
        mesh_cleanup(opt, last_step)
    else:
        mesh_cleanup_17(opt, last_step)


def mesh_cleanup(opt: Options, last_step: bool = False) -> None:
    if last_step:
        silence = ''
        context_merge_vertices = opt.last_step_merge_vertices
    else:
        silence = '!'
        context_merge_vertices = opt.merge_vertices
    lx.eval("{}mesh.cleanup {} {} {} {} {} {} {} {} {} {} {}".format(
            silence,
            f'floatingVertex:{opt.remove_floating_vertices}',
            f'onePointPolygon:{opt.remove_one_point_polygons}',
            f'twoPointPolygon:{opt.remove_two_points_polygons}',
            f'dupPointPolygon:{opt.fix_duplicate_points_in_polygon}',
            f'colinear:{opt.remove_colinear_vertices}',
            f'faceNormal:{opt.fix_face_normal_vectors}',
            f'mergeVertex:{context_merge_vertices}',
            f'mergeDisco:{opt.merge_disco_values}',
            f'unifyPolygon:{opt.unify_polygons}',
            f'forceUnify:{opt.force_unify}',
            f'removeDiscoWeight:{opt.remove_disco_weight_values}'
            ))


def mesh_cleanup_17(opt: Options, last_step: bool = False) -> None:
    if last_step:
        silence = ''
        context_merge_vertices = opt.last_step_merge_vertices
    else:
        silence = '!'
        context_merge_vertices = opt.merge_vertices
    lx.eval("{}mesh.cleanup {} {} {} {} {} {} {} {} {} {} {} {}".format(
            silence,
            f'floatingVertex:{opt.remove_floating_vertices}',
            f'onePointPolygon:{opt.remove_one_point_polygons}',
            f'twoPointPolygon:{opt.remove_two_points_polygons}',
            f'dupPointPolygon:{opt.fix_duplicate_points_in_polygon}',
            f'colinear:{opt.remove_colinear_vertices}',
            f'faceNormal:{opt.fix_face_normal_vectors}',
            f'mergeVertex:{context_merge_vertices}',
            f'mergeDisco:{opt.merge_disco_values}',
            f'unifyPolygon:{opt.unify_polygons}',
            f'forceUnify:{opt.force_unify}',
            f'removeDiscoWeight:{opt.remove_disco_weight_values}',
            f'fixGaps:{opt.fix_gaps}'
            ))


def main():
    print("")
    print("start mesh_islands_cleanup.py ...")

    opt = Options()
    opt.remove_floating_vertices = get_user_value(REMOVE_FLOATING_VERTICES)
    opt.remove_one_point_polygons = get_user_value(REMOVE_ONE_POINT_POLYGONS)
    opt.remove_two_points_polygons = get_user_value(REMOVE_TWO_POINTS_POLYGONS)
    opt.fix_duplicate_points_in_polygon = get_user_value(FIX_DUPLICATE_POINTS_IN_POLYGON)
    opt.remove_colinear_vertices = get_user_value(REMOVE_COLINEAR_VERTICES)
    opt.fix_face_normal_vectors = get_user_value(FIX_FACE_NORMAL_VECTORS)
    opt.merge_vertices = get_user_value(MERGE_VERTICES)
    opt.merge_disco_values = get_user_value(MERGE_DISCO_VALUES)
    opt.unify_polygons = get_user_value(UNIFY_POLYGONS)
    opt.force_unify = get_user_value(FORCE_UNIFY)
    opt.remove_disco_weight_values = get_user_value(REMOVE_DISCO_WEIGHT_VALUES)
    opt.fix_gaps = get_user_value(FIX_GAPS)
    opt.last_step_merge_vertices = get_user_value(LAST_STEP_MERGE_VERTICES)

    args = lx.args()
    if args:
        if args[0] == 'nofinal':
            opt.final_mesh_cleanup = False

    # get selected meshes
    selected_meshes: list[modo.Item] = scene.selectedByType(itype=c.MESH_TYPE)
    # cleanup selected meshes in a loop
    for mesh in selected_meshes:
        # group selected mesh in a temp folder
        mesh.select(replace=True)
        # get root index
        root_index = mesh.rootIndex
        parent_index = mesh.parentIndex
        mesh_index = root_index if root_index is not None else parent_index
        if not mesh_index:
            mesh_index = 0
        group_loc = scene.addItem(itype=c.GROUPLOCATOR_TYPE)
        group_loc.setParent(mesh.parent)
        mesh.setParent(group_loc)
        # unmerge mesh into a temp folder
        mesh.select(replace=True)
        lx.eval("layer.unmergeMeshes")
        # select all meshes in a folder
        for child in group_loc.children():
            child.select()
        # cleanup selected meshes
        mesh_cleanup_versions(opt)
        # merge selected meshes
        lx.eval("layer.mergeMeshes true")
        # parent mesh to an previous parent
        parent_item = group_loc.parent
        parent_id = parent_item.id if parent_item else None
        lx.eval("item.parent {} {} {} inPlace:1 duplicate:0".format(mesh.id, parent_id, mesh_index + 1))
        # remove a temp folder
        scene.removeItems(group_loc)

    # restore selection
    scene.deselect()
    for item in selected_meshes:
        item.select()

    # run one more Mesh Cleanup command with statistics
    if opt.final_mesh_cleanup:
        mesh_cleanup_versions(opt, last_step=True)

    print("mesh_islands_cleanup.py done.")


scene = modo.Scene()
log_name = replace_file_ext(scene.name)
h3dd = H3dDebug(enable=False, file=log_name)

if __name__ == "__main__":
    try:
        main()
    except H3dExitException as e:
        print(e.message)

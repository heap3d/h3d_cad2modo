#!/usr/bin/python
# ================================
# (C)2023-2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# mesh cleanup by mesh islands
# select mesh items and run the script

import webbrowser
from pathlib import Path

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import get_user_value, set_user_value


USERVAL_REMOVE_FLOATING_VERTICES = "h3d_imc_remove_floating_vertices"
USERVAL_REMOVE_ONE_POINT_POLYGONS = "h3d_imc_remove_one_point_polygons"
USERVAL_REMOVE_TWO_POINTS_POLYGONS = "h3d_imc_remove_two_points_polygons"
USERVAL_FIX_DUPLICATE_POINTS_IN_POLYGON = "h3d_imc_fix_duplicate_points_in_polygon"
USERVAL_REMOVE_COLINEAR_VERTICES = "h3d_imc_remove_colinear_vertices"
USERVAL_FIX_FACE_NORMAL_VECTORS = "h3d_imc_fix_face_normal_vectors"
USERVAL_MERGE_VERTICES = "h3d_imc_merge_vertices"
USERVAL_MERGE_DISCO_VALUES = "h3d_imc_merge_disco_values"
USERVAL_UNIFY_POLYGONS = "h3d_imc_unify_polygons"
USERVAL_FORCE_UNIFY = "h3d_imc_force_unify"
USERVAL_REMOVE_DISCO_WEIGHT_VALUES = "h3d_imc_remove_disco_weight_values"
USERVAL_LAST_STEP_MERGE_VERTICES = "h3d_imc_merge_vertices_last_step"
USERVAL_FIX_GAPS = "h3d_imc_fix_gaps"

USERVAL_ALARM_ENABLED = 'h3d_imc_alarm_enabled'
USERVAL_ALARM_SOUND_PATH = 'h3d_imc_alarm_path'

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


def main():
    print("")
    print("start mesh_islands_cleanup.py ...")

    options = Options()
    options.remove_floating_vertices = get_user_value(USERVAL_REMOVE_FLOATING_VERTICES)
    options.remove_one_point_polygons = get_user_value(USERVAL_REMOVE_ONE_POINT_POLYGONS)
    options.remove_two_points_polygons = get_user_value(USERVAL_REMOVE_TWO_POINTS_POLYGONS)
    options.fix_duplicate_points_in_polygon = get_user_value(USERVAL_FIX_DUPLICATE_POINTS_IN_POLYGON)
    options.remove_colinear_vertices = get_user_value(USERVAL_REMOVE_COLINEAR_VERTICES)
    options.fix_face_normal_vectors = get_user_value(USERVAL_FIX_FACE_NORMAL_VECTORS)
    options.merge_vertices = get_user_value(USERVAL_MERGE_VERTICES)
    options.merge_disco_values = get_user_value(USERVAL_MERGE_DISCO_VALUES)
    options.unify_polygons = get_user_value(USERVAL_UNIFY_POLYGONS)
    options.force_unify = get_user_value(USERVAL_FORCE_UNIFY)
    options.remove_disco_weight_values = get_user_value(USERVAL_REMOVE_DISCO_WEIGHT_VALUES)
    options.fix_gaps = get_user_value(USERVAL_FIX_GAPS)
    options.last_step_merge_vertices = get_user_value(USERVAL_LAST_STEP_MERGE_VERTICES)

    alarm_enabled = get_user_value(USERVAL_ALARM_ENABLED)
    alarm_sound_path = get_user_value(USERVAL_ALARM_SOUND_PATH)
    if alarm_enabled:
        if not (alarm_sound_path and Path(alarm_sound_path).is_file()):
            result = modo.dialogs.fileOpen(ftype='', title='Specify alarm path')
            if not result:
                print('Mesh Cleanup cancelled. Please select alarm file or turn alarm off.')
                return

            alarm_sound_path = str(result)
            set_user_value(USERVAL_ALARM_SOUND_PATH, alarm_sound_path)

    args = lx.args()
    if args:
        if args[0] == 'nofinal':
            options.final_mesh_cleanup = False

    selected_meshes: list[modo.Mesh] = modo.Scene().selectedByType(itype=c.MESH_TYPE)

    for mesh in selected_meshes:
        cleanup(mesh, options)

    modo.Scene().deselect()
    for item in selected_meshes:
        item.select()

    if alarm_enabled:
        webbrowser.open(alarm_sound_path)

    if options.final_mesh_cleanup:
        mesh_cleanup_versions(options, last_step=True)


def cleanup(mesh: modo.Mesh, options: Options):
    mesh.select(replace=True)

    root_index = mesh.rootIndex
    parent_index = mesh.parentIndex

    mesh_index = root_index if root_index is not None else parent_index
    if not mesh_index:
        mesh_index = 0

    tmp_loc = modo.Scene().addItem(itype=c.GROUPLOCATOR_TYPE)
    tmp_loc.setParent(mesh.parent)
    mesh.setParent(tmp_loc)

    mesh.select(replace=True)
    lx.eval("layer.unmergeMeshes")

    for child in tmp_loc.children():
        child.select()

    mesh_cleanup_versions(options)

    lx.eval("layer.mergeMeshes true")

    parent_item = tmp_loc.parent
    parent_id = parent_item.id if parent_item else None
    lx.eval("item.parent {} {} {} inPlace:1 duplicate:0".format(mesh.id, parent_id, mesh_index + 1))

    modo.Scene().removeItems(tmp_loc)


def mesh_cleanup_versions(opt: Options, last_step: bool = False) -> None:
    if lx.service.Platform().AppVersion() < 1700:  # type: ignore
        mesh_cleanup(opt, last_step)
    else:
        mesh_cleanup_17(opt, last_step)


def mesh_cleanup(opt: Options, last_step: bool = False) -> None:
    context_merge_vertices = opt.last_step_merge_vertices if last_step else opt.merge_vertices
    silent_mode = '' if last_step else '!'
    lx.eval("{}mesh.cleanup {} {} {} {} {} {} {} {} {} {} {}".format(
            silent_mode,
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
    context_merge_vertices = opt.last_step_merge_vertices if last_step else opt.merge_vertices
    silent_mode = '' if last_step else '!'
    lx.eval("{}mesh.cleanup {} {} {} {} {} {} {} {} {} {} {} {}".format(
            silent_mode,
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


if __name__ == "__main__":
    main()

#!/usr/bin/python
# ================================
# (C)2020 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# toybox
# assign each material in the library to corresponding polygon in 'material plate' mesh item
# ================================

import modo
import modo.constants as c
import lx


ARG_SELECTED = 'selected'


def get_selected_materials() -> list[modo.Item]:
    materials = []
    for material_mask in scene.selectedByType(itype='mask'):
        # get material_mask children
        if len(material_mask.childrenByType(c.ADVANCEDMATERIAL_TYPE)) > 0:
            materials.append(material_mask)

    return materials


def get_shader_tree_materials() -> list[modo.Item]:
    materials = []
    for material_mask in scene.items(itype='mask'):
        # get material_mask children
        if len(material_mask.childrenByType(c.ADVANCEDMATERIAL_TYPE)) > 0:
            materials.append(material_mask)

    return materials


def get_plate_mesh() -> modo.Item:
    meshes = scene.items("mesh", "material plate")
    if not meshes:
        # add unit plane item
        lx.eval('script.run "macro.scriptservice:32235733444:macro"')
        lx.eval('item.name "material plate" mesh')
        meshes = scene.items("mesh", "material plate")

    plate_mesh: modo.Item = meshes[0]
    plate_mesh.select(replace=True)
    if plate_mesh.parent:
        lx.eval("item.parent parent:{}")
    lx.eval("item.editorColor red")

    return plate_mesh


def subdivide_until(mesh: modo.Item, minimum_poly_count: int):
    """
        subdivide mesh until polygons count exceeds minimum_poly_count
    """
    mesh.select(replace=True)
    while len(mesh.geometry.polygons) < minimum_poly_count:
        lx.eval("poly.subdivide flat 0.0")


def fill_with_materials(mesh: modo.Item, materials: list[modo.Item]):
    mesh.select(replace=True)
    lx.eval("select.type polygon")
    for polygon in mesh.geometry.polygons:
        if polygon.index < len(materials):
            materialTag = materials[polygon.index].channel("ptag").get()

        #  select polygon and assign material to it
            polygon.select(replace=True)
            if not materialTag:
                continue
            lx.eval('poly.setMaterial "{}"'.format(materialTag))

    lx.eval("select.type item")


def main():
    selected = False
    args = lx.args()
    if args:
        selected = ARG_SELECTED in args

    if not selected:
        materials = get_shader_tree_materials()
    else:
        materials = get_selected_materials()

    material_plate_mesh = get_plate_mesh()

    subdivide_until(material_plate_mesh, len(materials))

    fill_with_materials(material_plate_mesh, materials)

    print("materials/polygons: {}/{}".format(len(materials), material_plate_mesh.geometry.numPolygons))


if __name__ == '__main__':
    print()
    print("material plate.py start...")

    scene = modo.Scene()
    main()

    print("material plate.py finished!")

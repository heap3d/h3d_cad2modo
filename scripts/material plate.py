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


print()
print("start...")

scene = modo.scene.current()
# get materials list
material_library = []
for material_mask in scene.items("mask"):
    # get material_mask children
    if len(material_mask.childrenByType(c.ADVANCEDMATERIAL_TYPE)) > 0:
        material_library.append(material_mask)

# get polygons list
meshes = scene.items("mesh", "material plate")
if not meshes:
    # add unit plane item
    lx.eval('script.run "macro.scriptservice:32235733444:macro"')
    # rename mesh
    lx.eval('item.name "material plate" mesh')
    meshes = scene.items("mesh", "material plate")

material_plate_mesh = meshes[0]  # type: modo.source_item.Mesh
material_plate_mesh.select(replace=True)
if material_plate_mesh.parent:
    lx.eval("item.parent parent:{}")
lx.eval("item.editorColor red")

# subdivide mesh until polygons count exceeds materials count
while len(material_plate_mesh.geometry.polygons) < len(material_library):
    lx.eval("poly.subdivide flat 0.0")

lx.eval("select.type polygon")
for polygon in material_plate_mesh.geometry.polygons:
    if polygon.index < len(material_library):
        materialTag = material_library[polygon.index].channel("ptag").get()

        #  select polygon and assign material to it
        polygon.select(replace=True)
        if not materialTag:
            continue
        lx.eval('poly.setMaterial "{}"'.format(materialTag))

print(
    "materials/polygons: {}/{}".format(
        len(material_library), material_plate_mesh.geometry.numPolygons
    )
)

print("finished!")

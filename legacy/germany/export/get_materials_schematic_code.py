#!/usr/bin/python
# ================================
# (C)2021 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# python
# EMAG
# set color for cad element by SAP material information
# this is how I see the process of assigning colors to parts of CAD model

T_PART = 'part'
T_ASSEMBLY = 'assembly'


class ElementClass:  # base class for part and assembly
    def __init__(self, element_type, element_id, cad_ref):
        self.id = element_id
        self.cad_ref = cad_ref
        self.type = element_type


class PartClass(ElementClass):  # NX part
    def __init__(self, part_id, cad_ref):
        ElementClass.__init__(self, element_type=T_PART, element_id=part_id, cad_ref=cad_ref)
        self.color = 'undefined'  # colors can be but not must be different for different part_id

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color


class AssemblyClass(ElementClass):  # NX assembly
    def __init__(self, asm_id, cad_ref):
        ElementClass.__init__(self, element_type=T_ASSEMBLY, element_id=asm_id, cad_ref=cad_ref)
        self.elements = set()

    def get_parts(self):
        parts_collection = set()
        # recursive call of get_elements()
        for item in self.elements:
            if item.type == T_PART:
                parts_collection.add(item)
            elif item.type == T_ASSEMBLY:
                parts_collection = parts_collection.union(item.get_parts())
            else:
                print ('type:{};   item id:{};   cad_ref:{};   item skipped.'.format(item.type, item.id, item.cad_ref))
        return parts_collection

    def add_element(self, element):
        if isinstance(element, ElementClass):
            self.elements.add(element)
        else:
            print ('add element failed:', element)


class SapDb:  # SAP database with access to materials and coatings
    def __init__(self):
        self.projects = dict()  # dictionary of projects; prj_name : root_asm
        self.materials = dict()  # dictionary of materials; part : material_id
        self.coatings = dict()  # dictionary of coatings; part : coating_id

    def add_project(self, project_name, root_assembly):
        if project_name in self.projects:
            print ('project already exist: ', project_name)
            return
        if isinstance(root_assembly, ElementClass):
            self.projects[project_name] = root_assembly
        else:
            print ('add project failed:', project_name)

    def set_material(self, part, mat_id):
        self.materials[part] = mat_id

    def get_material(self, part):
        return self.materials[part]

    def set_coating(self, part, coat_id):
        self.coatings[part] = coat_id

    def get_coating(self, part):
        return self.coatings[part]

    def get_surface(self, part):  # get coating or get material if coating not present
        surface = 'undefined'
        if part in self.materials:
            surface = self.materials[part]
        if part in self.coatings:
            surface = self.coatings[part]
        return surface

    def get_parts(self, project_name):
        return self.projects[project_name].get_parts()  # get parts from the root assembly

    @staticmethod
    def get_color_for_surface(surface):  # using constant surface > color assignment will be perfect
        # todo make constant surface-color relation
        # here I use random color assignment non related to surface just for working example
        return 'color_for_{}'.format(surface)


print()
print (')----- -----')
print ('start...')
print()

# create sample project

# fill database with elements
part1 = PartClass(part_id='part1', cad_ref='cad2')  # create part1
part2 = PartClass(part_id='part2', cad_ref='cad2')  # create part2, it referenced to the same cad item but have different attributes
part3 = PartClass(part_id='part3', cad_ref='cad4')  # create part3
part4 = PartClass(part_id='part4', cad_ref='cad4')  # create part4, undefined material
part_door_frame_left = PartClass('part_door_frame_left', 'cad_part_door_frame_left')
part_door_frame_right = PartClass('part_door_frame_right', 'cad_part_door_frame_right')
part_door_frame_glass = PartClass('part_door_frame_glass', 'cad_part_door_frame_glass')
part_screw1 = PartClass('screw1', 'cad_screw1')
part_screw2 = PartClass('screw2', 'cad_screw2')

asm1 = AssemblyClass(asm_id='asm1', cad_ref='cad1')  # create asm1
asm2 = AssemblyClass(asm_id='asm2', cad_ref='cad3')  # create asm2
asm1.add_element(element=part1)  # add part1 to asm1
asm2.add_element(element=part2)  # add part2 to asm2
asm1.add_element(element=part3)  # add part3 to asm1
asm1.add_element(element=part4)  # add part4 to asm1
asm1.add_element(element=asm2)  # add asm2 to asm1. assemblies can contain assemblies
asm_door_left = AssemblyClass('asm_door_left', 'cad_asm_door_left')
asm_door_left.add_element(part_door_frame_left)
asm_door_left.add_element(part_door_frame_glass)
asm_door_left.add_element(part_screw1)
asm_door_left.add_element(part_screw2)
asm_door_right = AssemblyClass('asm_door_right', 'cad_asm_door_right')
asm_door_right.add_element(part_door_frame_right)
asm_door_right.add_element(part_door_frame_glass)
asm_door_right.add_element(part_screw1)
asm_door_right.add_element(part_screw2)
asm_vl_mega = AssemblyClass('asm_vl_mega', 'cad_asm_vl_mega')
asm_vl_mega.add_element(asm1)
asm_vl_mega.add_element(asm_door_left)
asm_vl_mega.add_element(asm_door_right)

SAP_Info = SapDb()  # create database instance SAP_Info
SAP_Info.add_project('VL_Mega_Machine', asm_vl_mega)  # add project 'VL_Mega_Machine'
# link parts with materials and coatings
SAP_Info.set_material(part=part1, mat_id='white plastic')  # made from white plastic
SAP_Info.set_material(part2, 'white plastic')  # made from white plastic
SAP_Info.set_coating(part=part2, coat_id='green paint')  # part2 was made from white plastic but painted with green paint
SAP_Info.set_material(part3, 'ferro alloy #1')
SAP_Info.set_material(part_door_frame_left, 'ferro alloy #2')
SAP_Info.set_coating(part_door_frame_left, 'RAL#9010')
SAP_Info.set_material(part_door_frame_right, 'ferro alloy #2')
SAP_Info.set_coating(part_door_frame_right, 'RAL#9010')
SAP_Info.set_material(part_door_frame_glass, 'transparent tempered glass id#1')
SAP_Info.set_material(part_screw1, 'brass')
SAP_Info.set_material(part_screw2, 'aluminium')

# ----- -----
# get parts info from project and set colors for parts
surface_color_map = dict()  # dict of unique surfaces with mapped colors
for project_part in SAP_Info.get_parts(project_name='VL_Mega_Machine'):  # get project info
    part_surface = SAP_Info.get_surface(project_part)  # get surface for each part
    print ('part: {};   surface: {}'.format(project_part.id, part_surface))
    if part_surface not in surface_color_map:  # set part color for model export to the 3d team
        surface_color_map[part_surface] = SAP_Info.get_color_for_surface(part_surface)  # map new color to surface
        project_part.set_color(color=surface_color_map[part_surface])  # set color to part
    else:
        project_part.set_color(color=surface_color_map[part_surface])  # set existing color to part

# print surface-color map
print()
for proj_surface in surface_color_map:
    print ('{} = {}'.format(surface_color_map[proj_surface], proj_surface))

# todo write surface_color_map to the text file

print()
print ('done.')

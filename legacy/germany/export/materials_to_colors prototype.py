# ================================
# (C)2021 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# python
# EMAG
# materials to color prototype

# get project
SAP_project = SAP.get_project('VL_Mega')

# loop each part in the project, get surface linked to it, set part color by color mapped to surface
for part in SAP_project.get_all_parts:
    surface = SAP_project.get_surface_of_part(part)  # surface is an uncoated material (steel, aluminium, glass etc...) or coating (RAL9090, print etc...)
    color = SAP_project.get_color_by_surface(surface)  # get color mapped to surface (color#1 for steel, color#2 for RAL9090 etc...)
    SAP_project.set_part_color(part, color)  # set mapped color to part
    
# todo export CAD model with mapped colors assigned
# todo save color-surface map to the .txt file using line template: 'color_str = surface_str'

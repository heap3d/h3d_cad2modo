#!/usr/bin/python
# ================================
# (C)2021 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# nx color map

import modo
import modo.constants as c

scene = modo.scene.current()

# mask_list = set()
auto_marker = '#auto# '
filename = 'D:/work/scripts/modo/h3d tools/cad2modo/germany/3dmatlist.txt'


def get_mask_list():
    mask_collection = list()
    for mat_mask in scene.items(itype=c.MASK_TYPE):
        if mat_mask.name.startswith(auto_marker):
            continue
        if mat_mask.channel('ptyp') is None:
            continue
        if mat_mask.channel('ptyp').get() != 'Material':
            continue
        if mat_mask.channel('ptag').get() == '':
            continue
        # add mask name string to list
        ptag_str = '{}'.format(mat_mask.channel('ptag').get())
        mask_collection.append(ptag_str)
    return mask_collection


print
print 'start...'
# ------ ------

# get material mask list except #auto#
mask_list = get_mask_list()

f = open(filename, 'w')

try:
    for index, mask_str in enumerate(mask_list):
        out_str = 'color #{} = {}'.format(index, mask_str)
        print out_str
        f.write(out_str + '\n')
except IOError:
    print IOError.message
finally:
    f.close()

# ------ ------
print 'done.'

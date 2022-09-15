#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get default map table path
# ================================

import lx
import modo

USERVAL_NAME_DEF_MAP_PATH = 'h3d_rtu_default_map_path'

# initialize filename
filename = lx.eval('user.value {} ?'.format(USERVAL_NAME_DEF_MAP_PATH))

dialog_result = modo.dialogs.fileOpen(ftype='text', path=filename)
if dialog_result:
    lx.eval('user.value {} "{}"'.format(USERVAL_NAME_DEF_MAP_PATH, dialog_result))

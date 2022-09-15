#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get directory
# ================================

import lx
import modo

USER_VAL_REFLIB_DIR_NAME = 'h3d_opma_reflib_dir'

# initialize dir_path
filename = lx.eval('user.value {} ?'.format(USER_VAL_REFLIB_DIR_NAME))

dialog_result = modo.dialogs.dirBrowse(title='Select Reference Library Directory', path=filename)
if dialog_result:
    lx.eval('user.value {} "{}"'.format(USER_VAL_REFLIB_DIR_NAME, dialog_result))

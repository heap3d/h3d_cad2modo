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

USER_VAL_STORE_DIR_NAME = 'h3d_opma_store_dir'

# initialize dir_path
filename = lx.eval('user.value {} ?'.format(USER_VAL_STORE_DIR_NAME))

dialog_result = modo.dialogs.dirBrowse(title='Select Store Directory', path=filename)
if dialog_result:
    lx.eval('user.value {} "{}"'.format(USER_VAL_STORE_DIR_NAME, dialog_result))

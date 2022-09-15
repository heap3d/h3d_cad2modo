#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get image filename
# ================================

import lx
import modo

USER_VAL_NAME_ENV_PATH_NAME = 'h3d_opma_env_path'

# initialize filename
filename = lx.eval('user.value {} ?'.format(USER_VAL_NAME_ENV_PATH_NAME))

dialog_result = modo.dialogs.fileOpen(ftype='image', path=filename)
if dialog_result:
    lx.eval('user.value {} "{}"'.format(USER_VAL_NAME_ENV_PATH_NAME, dialog_result))

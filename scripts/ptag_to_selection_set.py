import modo
import lx
import modo.constants as c


def ptag_to_selection_set(rgb_color_strings, prefix_to_ignore):
    # select all mesh items and enter polygon mode to selection sets creation
    modo.scene.current().deselect()
    # enter item mode
    lx.eval('select.type item')
    # select all meshes
    for item in modo.scene.current().items(itype=c.MESH_TYPE):
        item.select()

    # convert ptag sets into polygon selection sets
    for color_str in rgb_color_strings:
        modo.scene.current().deselect()

        # drop polygon selection
        lx.eval('select.drop polygon')

        for ptag in rgb_color_strings[color_str]:
            for mask in modo.scene.current().items(itype='mask'):
                if mask.channel('ptyp') is None:
                    continue

                if mask.channel('ptyp').get() != 'Material':
                    continue

                if str(mask.name).startswith(prefix_to_ignore):
                    continue

                if mask.channel('ptag').get() == ptag:
                    mask.select()

        # select poly by material
        lx.eval('material.selectPolygons')
        # create polygon selection set
        lx.eval('select.editSet "{}" add'.format(color_str))
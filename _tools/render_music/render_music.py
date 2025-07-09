# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


import bpy, aud
from bpy.app.handlers import persistent

@persistent
def play_music(scene):
    handle = bpy.types.RenderSettings.music_handle
    # addon_prefs = bpy.context.user_preferences.addons[__package__].preferences
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    if addon_prefs.use_play:
        if not hasattr(handle, "status") or (hasattr(handle, "status") and handle.status == False):
            print("Playing elevator music...")
            # device = aud.device()
            # factory = aud.Factory(addon_prefs.playfile)
            # bpy.types.RenderSettings.music_handle = device.play(factory)
            # handle.loop_count = -1
            device = aud.Device()
            playMusic = aud.Sound.file(addon_prefs.playfile)
            bpy.types.RenderSettings.music_handle = device.play(playMusic)
            bpy.types.RenderSettings.music_handle.loop_count = -1

@persistent
def kill_music(scene):
    handle = bpy.types.RenderSettings.music_handle

    if hasattr(handle, "status") and handle.status == True:
        print("Killing elevator music...")
        handle.stop()

@persistent
def end_music(scene):
    handle = bpy.types.RenderSettings.music_handle
    # addon_prefs = bpy.context.user_preferences.addons[__package__].preferences
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    
    kill_music(scene)
    
    if addon_prefs.use_end:
        # device = aud.device()
        # factory = aud.Factory(addon_prefs.endfile)
        # bpy.types.RenderSettings.music_handle = device.play(factory)
        device = aud.Device()
        endMusic = aud.Sound.file(addon_prefs.endfile)
        bpy.types.RenderSettings.music_handle = device.play(endMusic)

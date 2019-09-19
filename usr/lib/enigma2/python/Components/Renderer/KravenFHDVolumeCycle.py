# -*- coding: utf-8 -*-

#  Volume Cycle Renderer
#
#  Coded/Modified/Adapted by Team Kraven
#  Based on VTi and/or OpenATV image source code
#
#  This code is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ 
#  or send a letter to Creative Commons, 559 Nathan 
#  Abbott Way, Stanford, California 94305, USA.
#
#  If you think this license infringes any rights,
#  please contact Team Kraven at info@coolskins.de

from Renderer import Renderer
from enigma import ePixmap, eTimer, eDVBVolumecontrol

class KravenFHDVolumeCycle(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.vol_timer = eTimer()
        self.vol_timer.callback.append(self.pollme)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.suspended:
            value = str(eDVBVolumecontrol.getInstance().getVolume())
            self.instance.setPixmapFromFile('/usr/share/enigma2/KravenFHD/volume/' + value + '.png')

    def pollme(self):
        self.changed(None)
        return

    def onShow(self):
        self.suspended = False
        self.vol_timer.start(200)

    def onHide(self):
        self.suspended = True
        self.vol_timer.stop()
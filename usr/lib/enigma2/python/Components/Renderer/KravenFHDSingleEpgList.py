# -*- coding: utf-8 -*-

#  Single EPG List Renderer
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

from Components.VariableText import VariableText
from enigma import eLabel, eEPGCache
from Renderer import Renderer
from time import localtime

class KravenFHDSingleEpgList(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.epgcache = eEPGCache.getInstance()

    GUI_WIDGET = eLabel

    def changed(self, what):
        event = self.source.event
        if event is None:
            self.text = ''
            return
        else:
            service = self.source.service
            text = ''
            evt = None
            if self.epgcache is not None:
                evt = self.epgcache.lookupEvent(['IBDCT', (service.toString(),
                  0,
                  -1,
                  -1)])
            if evt:
                maxx = 0
                for x in evt:
                    if maxx > 0:
                        if x[4]:
                            t = localtime(x[1])
                            text = text + '%02d:%02d %s\n' % (t[3], t[4], x[4])
                        else:
                            text = text + 'n/a\n'
                    maxx += 1
                    if maxx > 15:
                        break

            self.text = text
            return
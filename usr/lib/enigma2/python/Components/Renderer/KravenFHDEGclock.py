# -*- coding: utf-8 -*-

#  EG Clock Renderer
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

from Components.VariableValue import VariableValue
from Renderer import Renderer
from enigma import eGauge

class KravenFHDEGclock(VariableValue, Renderer):

    def __init__(self):
        Renderer.__init__(self)
        VariableValue.__init__(self)

    GUI_WIDGET = eGauge

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            return
        else:
            value = self.source.value
            if value is None:
                value = 0
            self.setValue(value)
            return

    GUI_WIDGET = eGauge

    def postWidgetCreate(self, instance):
        instance.setValue(0)

    def setValue(self, value):
        if self.instance is not None:
            self.instance.setValue(value)
        return
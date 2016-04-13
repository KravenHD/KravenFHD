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
#
#  Menu MiniTV Renderer
#  Based on OpenATV Picture in Graphics Renderer
#  Modified by tomele for Kraven Skins
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan
#  Abbott Way, Stanford, California 94305, USA.
#
#  This plugin is NOT free software. It is open source,
#  you are allowed to modify it (if you keep the license),
#  but it may not be commercially distributed other than
#  under the conditions noted above.
#

from Renderer import Renderer
from enigma import eVideoWidget, getDesktop, eTimer
from Screens.PictureInPicture import PipPigMode
from Components.config import config

class KravenFHDMenuPig(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.Position = self.Size = None
		self.hidePip = True
		return

	GUI_WIDGET = eVideoWidget

	def debug(self,what):
		f=open('/tmp/kraven_debug.txt','a+')
		f.write(str(what)+'\n')
		f.close()
		
	def postWidgetCreate(self, instance):
		desk = getDesktop(0)
		instance.setDecoder(0)
		instance.setFBSize(desk.size())

	def applySkin(self, desktop, parent):
		attribs = self.skinAttributes[:]
		for attrib, value in self.skinAttributes:
			if attrib == 'hidePip':
				self.hidePip = value == 1
				attribs.remove((attrib, value))

		self.skinAttributes = attribs
		ret = Renderer.applySkin(self, desktop, parent)
		if ret:
			self.Position = self.instance.position()
			self.Size = self.instance.size()
		return ret

	def onShow(self):
		if self.instance:
			config.plugins.KravenFHD.PigMenuActive.value = True
			config.plugins.KravenFHD.PigMenuActive.save()
			if self.Size:
				self.instance.resize(self.Size)
			if self.Position:
				self.instance.move(self.Position)
			self.hidePip and PipPigMode(True)

	def onHide(self):
		if self.instance:
			self.preWidgetRemove(self.instance)
			self.hidePip and PipPigMode(False)
			config.plugins.KravenFHD.PigMenuActive.value = False
			config.plugins.KravenFHD.PigMenuActive.save()

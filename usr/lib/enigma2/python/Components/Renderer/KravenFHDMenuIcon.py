from Renderer import Renderer
from enigma import ePixmap,eTimer
import os

class KravenFHDMenuIcon(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.scale = '0'

	def applySkin(self, desktop, parent):
		attribs = [ ]
		for (attrib, value) in self.skinAttributes:
			if attrib == 'noscale':
				self.scale = value
			else:
				attribs.append((attrib,value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def postWidgetCreate(self, instance):
		self.changed((self.CHANGED_DEFAULT,))

	def changed(self, what):
		if what[0] != self.CHANGED_CLEAR:
			if self.instance:
				pngname=self.source.text
				if self.scale is '0':
					self.instance.setScale(1)
				self.instance.setPixmapFromFile(pngname)
				self.instance.show()

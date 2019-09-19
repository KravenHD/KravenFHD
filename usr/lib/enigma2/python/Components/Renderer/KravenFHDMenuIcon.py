# -*- coding: utf-8 -*-

#  Menu Icon Renderer
#
#  Coded/Modified/Adapted by Team Kraven
#  Based on VTi and/or OpenATV image source code
#  Based on the work of shamann (see below)
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

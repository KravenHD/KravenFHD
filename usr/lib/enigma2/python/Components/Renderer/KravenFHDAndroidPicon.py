# -*- coding: utf-8 -*-

#  Android Picon Renderer
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
from enigma import ePixmap
from Components.config import config
from Tools.Directories import fileExists, SCOPE_CURRENT_SKIN, resolveFilename 

class KravenFHDAndroidPicon(Renderer):

	__module__ = __name__
	def __init__(self):
		Renderer.__init__(self)
		self.pngname = ''

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if attrib == 'path':
				self.path = value
			else:
				attribs.append((attrib, value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			if self.path:
                           self.pngname = '/usr/share/enigma2/KravenFHD/' + self.path + '/' + str(self.source.text) + '.png'
                           if not fileExists(self.pngname):
                              self.pngname = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
                           self.instance.setScale(1)
                           self.instance.setPixmapFromFile(self.pngname)

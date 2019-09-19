# -*- coding: utf-8 -*-

#  Empty EPG Renderer
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
#
#  Original License:

#######################################################################
#
#    Renderer for Enigma2
#    Coded by shamann (c)2016
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#######################################################################

from Renderer import Renderer
from enigma import eLabel, eTimer, eSize
from Components.VariableText import VariableText
from Components.config import config
from skin import parseFont

class KravenFHDEmptyEpg(VariableText, Renderer):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.EmptyText = ""
		self.fillTimer = eTimer()
		try:
			self.fillTimer_conn = self.fillTimer.timeout.connect(self.__fillText)
		except AttributeError:
			self.fillTimer.timeout.get().append(self.__fillText)
		self.backText = ""
		self.vvv = ""
		self.testSizeLabel = None
    		
	def applySkin(self, desktop, parent):
		attribs = [ ]
		for (attrib, value) in self.skinAttributes:
			if attrib == "size":
				self.sizeX = int(value.strip().split(",")[0])
				attribs.append((attrib,value))
			elif attrib == "emptyText":
				self.EmptyText = value
			elif attrib == "font":
				self.used_font = parseFont(value, ((1,1),(1,1)))
				attribs.append((attrib,value))
			else:
				attribs.append((attrib,value))
		self.skinAttributes = attribs
		self.testSizeLabel.setFont(self.used_font)
		self.testSizeLabel.resize(eSize(self.sizeX+500,20))
		self.testSizeLabel.setVAlign(eLabel.alignTop)
		self.testSizeLabel.setHAlign(eLabel.alignLeft)
		self.testSizeLabel.setNoWrap(1)
		return Renderer.applySkin(self, desktop, parent)
		
	GUI_WIDGET = eLabel

	def connect(self, source):
		Renderer.connect(self, source)
		self.changed((self.CHANGED_DEFAULT,))
		
	def changed(self, what):
		if what[0] == self.CHANGED_CLEAR:
			self.text = ""
		else:
			self.text = self.source.text
			if self.instance and self.backText != self.text:
				if self.text == "":
					self.text = self.EmptyText
				tmp = self.text
				self.testSizeLabel.setText(tmp)
				text_width = self.testSizeLabel.calculateSize().width()
				if text_width > (self.sizeX - 30):
					while (text_width > (self.sizeX - 30)):
						tmp = tmp[:-1]
						self.testSizeLabel.setText(tmp)
						text_width = self.testSizeLabel.calculateSize().width()
					pos = tmp.rfind(' ')
					if pos != -1:
						tmp = tmp[:pos].rstrip(' ') + "..."
					self.text = tmp
				if self.backText != self.text:
					self.backText = self.text
					ena = True
					try:
						if config.plugins.KravenFHD.TypeWriter.value == "typewriter":
							ena = True
						else:
							ena = False
					except:
						pass
					if ena:
						self.text = "_"
						self.endPoint = len(self.backText)
						self.posIdx = 0
						if self.fillTimer.isActive():
							self.fillTimer.stop()
						self.fillTimer.start(1300, True)
					
	def __fillText(self):
		self.fillTimer.stop()
		self.posIdx += 1
		if self.posIdx <= self.endPoint:
			self.text = self.backText[:self.posIdx] + "_"
			self.fillTimer.start(50, True)
		else:
			self.text = self.backText 					
					
	def preWidgetRemove(self, instance):
		self.testSizeLabel = None

	def postWidgetCreate(self, instance):
		self.testSizeLabel = eLabel(instance)
		self.testSizeLabel.hide()
		

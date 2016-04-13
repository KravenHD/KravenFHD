#
#  MiniTV Renderer
#  Based on P(icture)i(n)g(raphics) renderer by VTi-Team
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
from enigma import eVideoWidget,eTimer,getDesktop,eServiceCenter,iServiceInformation
from Screens.InfoBar import InfoBar
from Components.SystemInfo import SystemInfo
from Components.config import config
from enigma import eActionMap

fbtool=None
init_PiG=None
fb_size_history=[]

class KravenFHDPig3(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		global fbtool
		fbtool=KravenFBHelper()
		self.Position=self.Size=None
		self.decoder=0
		self.fb_w = getDesktop(0).size().width()
		self.fb_h = getDesktop(0).size().height()
		self.fb_size = None
		self._del_pip = False
		self._can_extended_PiG = False
		self.first_PiG = False
		self.is_channelselection = False

	GUI_WIDGET = eVideoWidget

	def postWidgetCreate(self, instance):
		self.prev_fb_info = fbtool.getFBSize()
		desk = getDesktop(0)
		instance.setDecoder(self.decoder)
		instance.setFBSize(desk.size())
		self.this_instance = instance

	def applySkin(self, desktop, parent):
		if self.skinAttributes is not None:
			attribs = []
			for (attrib, value) in self.skinAttributes:
				if attrib == "OverScan":
					if value.lower() == "false" or value == "0":
						self.instance.setOverscan(False)
				else:
					attribs.append((attrib, value))
				if attrib == "position":
					x = value.split(',')[0]
					y = value.split(',')[1]
				elif attrib == "size":
					w = value.split(',')[0]
					h = value.split(',')[1]
			self.skinAttributes = attribs
			x = format(int(float(x) / self.fb_w * 720.0), 'x').zfill(8)
			y = format(int(float(y) / self.fb_h * 576.0), 'x').zfill(8)
			w = format(int(float(w) / self.fb_w * 720.0), 'x').zfill(8)
			h = format(int(float(h) / self.fb_h * 576.0), 'x').zfill(8)
			self.fb_size = [w, h, x, y]
				
		ret = Renderer.applySkin(self, desktop, parent)
		if ret:
			self.Position = self.instance.position()
			self.Size = self.instance.size()
		return ret

	def onShow(self):
		fbtool.is_PiG = True
		if self.instance:
			if self.Size:
				self.instance.resize(self.Size)
			if self.Position:
				self.instance.move(self.Position)
			if InfoBar.instance and InfoBar.instance.session.pipshown and not InfoBar.instance.session.is_audiozap:
				fbtool.setFBSize(['00000001','00000001','00000000','00000000'],decoder=1)
				if self.fb_size:
					fbtool.setFBSize(self.fb_size, self.decoder)

	def onHide(self):
		if self.instance:
			fbtool.is_PiG = False
			self.preWidgetRemove(self.instance)
			if InfoBar.instance and InfoBar.instance.session.pipshown and InfoBar.instance.session.is_splitscreen:
				self.prev_fb_info = InfoBar.instance.session.pip.prev_fb_info
				self.prev_fb_info_second_dec = InfoBar.instance.session.pip.prev_fb_info_second_dec
				fbtool.setFBSize(self.prev_fb_info_second_dec, decoder = 1)
				fbtool.setFBSize_delayed(self.prev_fb_info, decoder = 0, delay = 200)
			elif InfoBar.instance and InfoBar.instance.session.pipshown and not InfoBar.instance.session.is_splitscreen and not InfoBar.instance.session.is_audiozap and not InfoBar.instance.session.is_pig:
				self.prev_fb_info = InfoBar.instance.session.pip.prev_fb_info
				fbtool.setFBSize_delayed(self.prev_fb_info, decoder = 1, delay = 200)

	def destroy(self):
		if self.first_PiG and InfoBar.instance.session.pipshown:
			global init_PiG
			init_PiG = False
			if InfoBar.instance and InfoBar.instance.session.is_pig:
				InfoBar.instance.showPiP()
		self.__dict__.clear()

class KravenFBHelper:
	def __init__(self):
		self.fb_proc_path="/proc/stb/vmpeg"
		self.fb_info=["dst_width","dst_height","dst_left","dst_top"]
		self.new_fb_size_pos=None
		self.decoder=None
		self.delayTimer=None
		self.is_PiG=False

	def getFBSize(self,decoder=0):
		ret=[]
		for val in self.fb_info:
			try:
				f=open("%s/%d/%s" % (self.fb_proc_path,decoder,val),"r")
				fb_val=f.read().strip()
				ret.append(fb_val)
				f.close()
			except IOError:
				pass
		if len(ret)==4:
			return ret
		return None

	def setFBSize(self,fb_size_pos,decoder=0,force=False):
		if self.delayTimer:
			self.delayTimer.stop()
		if (InfoBar.instance and InfoBar.instance.session.pipshown) or force:
			if fb_size_pos and len(fb_size_pos)>=4:
				i=0
				for val in self.fb_info:
					try:
						f=open("%s/%d/%s" % (self.fb_proc_path,decoder,val),"w")
						fb_val=fb_size_pos[i]
						f.write(fb_val)
						f.close()
					except IOError:
						pass
					i+=1
				for val in ("00000001","00000000"):
					try:
						f=open("%s/%d/%s" % (self.fb_proc_path,decoder,"dst_apply"),"w")
						f.write(val)
						f.close()
					except IOError:
						pass

	def delayTimerFinished(self):
		fb_size_pos=self.new_fb_size_pos
		decoder=self.decoder
		self.new_fb_size_pos=None
		self.decoder=None
		if not self.is_PiG:
			self.setFBSize(fb_size_pos,decoder)

	def setFBSize_delayed(self,fb_size_pos,decoder=0,delay=1000):
		if fb_size_pos and len(fb_size_pos)>=4:
			self.new_fb_size_pos=fb_size_pos
			self.decoder=decoder
			self.delayTimer=eTimer()
			self.delayTimer.callback.append(self.delayTimerFinished)
			self.delayTimer.start(delay)


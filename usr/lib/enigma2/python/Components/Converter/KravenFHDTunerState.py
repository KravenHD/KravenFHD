# -*- coding: utf-8 -*-

#  Tuner State Converter
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

from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll

from Components.Sources.TunerInfo import TunerInfo
from enigma import iServiceInformation
import NavigationInstance

class KravenFHDTunerState(Poll, Converter, object):

	def __init__(self, type):
	
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.poll_interval = 1000
		self.poll_enabled = True
		
		inputlist = type.split(",")
		typelist = inputlist[0].split("_")
		
		self.query = typelist[0]
		
		self.boxnum = 0
		if len(typelist) > 1:
			self.boxnum = int(typelist[1])
		
		self.boxcount = 0
		if len(typelist) > 2:
			self.boxcount = int(typelist[2])
					
		self.showunused = False
		self.streamastuner = False
		for arg in inputlist:
			if arg == "ShowUnused":
				self.showunused = True
			if arg == "StreamAsTuner":
				self.streamastuner = True
			
	@cached
	def getBoolean(self):
	
		self.getBoxes()
		
		if self.query == "IsActive":
			if self.box >= 0 and self.box < self.activetuners:
				return True
			else:
				return False
			
		elif self.query == "IsAvailable":
			if self.showunused and self.box >= 0 and self.box >= self.activetuners and self.box < self.availabletuners:
				return True
			else:
				return False
				
		elif self.query == "IsStreamActive":
			return (self.streamactive or self.streamrecord)
							
		elif self.query == "IsStreamAvailable":
			return self.showunused and not (self.streamactive or self.streamrecord)
							
	boolean = property(getBoolean)
	
	@cached
	def getText(self):
	
		self.getBoxes()

		if self.query == "StreamText":
		
			if self.availabletuners == 1:
				txt = "Stream"
			else:
				txt = "@"

			if self.streamactive and self.streamrecord:
				col = "X"
			elif self.streamactive:
				col = "L"
			elif self.streamrecord:
				col = "R"
			else:
				txt = ""
				col = "T"
				
			return txt + "_" + col
		
		else:
		
			if self.box >= 0 and self.activetuners > 0 and self.box < self.activetuners:
				num = self.boxes[self.box].split("_")[0]
				col = self.boxes[self.box].split("_")[1]
				
				if num == "99":
					tun = "@"
				else:
					tun = chr(int(num) + 65)
				
				if tun == "A" and self.availabletuners == 1:
					tun = "Tuner"

				return tun + "_" + col
				
			else:
				return "_T"
			
	text = property(getText)
	
	def getBoxes(self):
	
		self.streamactive = False
		self.streamrecord = False
		
		boxes = []
		
		# busy tuners
		mask = self.source.getTunerUseMask()
		mcnt = 0
		while mask:
			if mask & 1 == 1:
				boxes.append(str(mcnt) + "_B")
			mask //= 2
			mcnt += 1

		# recording tuners
		for timer in NavigationInstance.instance.RecordTimer.timer_list:
			if timer.isRunning() and not timer.justplay:
				service = timer.record_service
				feinfo = service and service.frontendInfo()
				data = feinfo and feinfo.getFrontendData()
				if data:
					tuner = data.get('tuner_number', -1)
					if tuner is not None and tuner > -1:
						if boxes.count(str(tuner) + "_B") > 0:
							boxes.remove(str(tuner) + "_B")
						if boxes.count(str(tuner) + "_R") < 1:
							boxes.append(str(tuner) + "_R")
				else:
					self.streamrecord = True
					if self.streamastuner:
						boxes.append("99_R")

		# current tuner
		service = NavigationInstance.instance.getCurrentService()
		feinfo = service and service.frontendInfo()
		data = feinfo and feinfo.getFrontendData()
		if data:
			tuner = data.get('tuner_number', -1)
			if tuner is not None and tuner > -1:
				if boxes.count(str(tuner) + "_B") > 0:
					boxes.remove(str(tuner) + "_B")
					boxes.append(str(tuner) + "_L")
				if boxes.count(str(tuner) + "_R") > 0:
					boxes.remove(str(tuner) + "_R")
					boxes.append(str(tuner) + "_X")
		else:			
			info = service and service.info()
			
			if info:
				if self.getE2DistroVersion() == "VTi":
					self.streamactive = info.getInfo(iServiceInformation.sIsIPStream) == 1
				else:
					self.streamactive = service.streamed() is not None
					
				if self.streamastuner and self.streamactive:
					if boxes.count("99_R") > 0:
						boxes.remove("99_R")
						boxes.append("99_X")
					else:
						boxes.append("99_L")
		
		boxes.sort(key=self.intFirst)
		
		self.boxes = boxes
		self.activetuners = len(boxes)
		self.availabletuners = self.source.getTunerAmount() + int(self.streamastuner)
		
		self.box = self.boxnum
		if self.boxcount > 0:
			if self.showunused:
				self.box -= (self.boxcount - self.availabletuners)
			else:
				self.box -= (self.boxcount - self.activetuners)
				
	def getE2DistroVersion(self):
		try:
			from boxbranding import getImageDistro
			if getImageDistro() == "openatv":
				return "openatv"
			elif getImageDistro() == "teamblue":
				return "teamblue"
			elif getImageDistro() == "VTi":
				return "VTi"
		except ImportError:
			return "VTi"
			
	def intFirst(self,elem):
		return int(elem.split("_")[0])

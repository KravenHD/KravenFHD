# -*- coding: utf-8 -*-
#
#  RealTek Weather Info
#
#  Coded by TBX for Kraven Skins (c) 2016
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#

from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Converter.Converter import Converter
from Components.Language import language
from Components.Element import cached
from Components.config import config
from xml.etree.cElementTree import fromstring
from enigma import eTimer
from datetime import datetime
import os, gettext, requests
from Poll import Poll
from Plugins.Extensions.KravenFHD import ping

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("KravenFHD", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/KravenFHD/locale/"))

def _(txt):
	t = gettext.dgettext("KravenFHD", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

URL = 'http://realtek.accu-weather.com/widget/realtek/weather-data.asp?%s' % str(config.plugins.KravenFHD.weather_realtek_latlon.value)
WEATHER_DATA = None
WEATHER_LOAD = True

class KravenFHDWeather_realtek(Poll, Converter, object):
	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.poll_interval = 60000
		self.poll_enabled = True
		type = type.split(',')
		self.day_value = type[0]
		self.what = type[1]
		self.data = {}
		self.timer = eTimer()
		self.timer.callback.append(self.reset)
		self.timer.callback.append(self.get_Data)
		self.data = None
		self.get_Data()

	@cached
	def getText(self):
		global WEATHER_DATA
		self.data = WEATHER_DATA
		day = self.day_value.split('_')[1]
		if self.what == 'DayTemp':
			self.info = self.getDayTemp()
		elif self.what == 'FeelTemp':
			self.info = self.getFeelTemp()
		elif self.what == 'MinTemp':
			self.info = self.getMinTemp(int(day))
		elif self.what == 'MaxTemp':
			self.info = self.getMaxTemp(int(day))
		elif self.what == 'MinMaxTemp':
			if self.getMinTemp(int(day)) == '' or self.getMaxTemp(int(day)) == '':
				self.info = ''
			else:
				self.info = self.getMinTemp(int(day))+" / "+self.getMaxTemp(int(day))
		elif self.what == 'Description':
			self.info = self.getWeatherDes(int(day))
		elif self.what == 'MeteoIcon':
			self.info = self.getWeatherIcon(int(day))
		elif self.what == 'MeteoFont':
			self.info = self.getMeteoFont(int(day))
		elif self.what == 'WetterDate':
			self.info = self.getWeatherDate(int(day))
		elif self.what == 'Wind':
			self.info = self.getCompWind()
		elif self.what == 'Humidity':
			self.info = self.getHumidity()
		elif self.what == 'RainMM':
			self.info = self.getRainMM(int(day))
		elif self.what == 'City':
			self.info = str(config.plugins.KravenFHD.weather_foundcity.getValue())
		return str(self.info)

	text = property(getText)

	def reset(self):
		global WEATHER_LOAD
		WEATHER_LOAD = True
		self.timer.stop()

	def get_Data(self):
		global WEATHER_DATA
		global WEATHER_LOAD
		if WEATHER_LOAD == True:
			try:
				r = ping.doOne("8.8.8.8",1.5)
				if r != None and r <= 1.5:
					print "KravenWeather: Weather download from RealTek"
					self.data = {}
					index = 0
					res = requests.get(URL, timeout=1.5)
					root = fromstring(res.text.replace('xmlns="http://www.accuweather.com"',''))
					for child in root.findall('currentconditions'):
						self.data['Day_%s' % str(index)] = {}
						self.data['Day_%s' % str(index)]['temp'] = child.find('temperature').text
						self.data['Day_%s' % str(index)]['skytextday'] = child.find('weathertext').text
						self.data['Day_%s' % str(index)]['skycodeday'] = child.find('weathericon').text
						self.data['Day_%s' % str(index)]['humidity'] = child.find('humidity').text
						self.data['Day_%s' % str(index)]['winddisplay'] = child.find('winddirection').text
						self.data['Day_%s' % str(index)]['windspeed'] = child.find('windspeed').text
						self.data['Day_%s' % str(index)]['feelslike'] = child.find('realfeel').text
					for child in root.findall('forecast'):
						for item in child.findall('day'):
							for entrie in item.findall('daytime'):
								if index > 0:
									self.data['Day_%s' % str(index)] = {}
									self.data['Day_%s' % str(index)]['skycodeday'] = entrie.find('weathericon').text
									self.data['Day_%s' % str(index)]['skytextday'] = entrie.find('txtshort').text
								self.data['Day_%s' % str(index)]['day'] = item.find('obsdate').text
								self.data['Day_%s' % str(index)]['low'] = entrie.find('lowtemperature').text
								self.data['Day_%s' % str(index)]['high'] = entrie.find('hightemperature').text
								self.data['Day_%s' % str(index)]['precip'] = entrie.find('rainamount').text
								index += 1
					WEATHER_DATA = self.data
					WEATHER_LOAD = False
			except:
				pass
			timeout = max(15,int(config.plugins.KravenFHD.refreshInterval.value)) * 1000.0 * 60.0
			self.timer.start(int(timeout), True)
		else:
			self.data = WEATHER_DATA

	def getMinTemp(self, day):
		try:
			temp = self.data['Day_%s' % str(day)]['low']
			if temp == '':
				return temp
			return str(temp) + '°'
		except:
			return ''

	def getMaxTemp(self, day):
		try:
			temp = self.data['Day_%s' % str(day)]['high']
			if temp == '':
				return temp
			return str(temp) + '°'
		except:
			return ''

	def getFeelTemp(self):
		try:
			temp = self.data['Day_0']['temp']
			feels = self.data['Day_0']['feelslike']
			return str(int(temp)) + '°C' + _(", feels ") + str(int(feels)) + '°C'
		except:
			return 'N/A'

	def getDayTemp(self):
		try:
			temp = self.data['Day_0']['temp']
			return str(temp) + '°C'
		except:
			return 'N/A'

	def getWeatherDes(self, day):
		try:
			weather = self.data['Day_%s' % str(day)]['skytextday']
			weather = weather.replace("Ã¤","ä")
			weather = weather.replace("Ã¶","ö")
			weather = weather.replace("Ã¼","ü")
			weather = weather.replace("ÃŸ","ß")
			weather = weather.replace("Ã„","Ä")
			weather = weather.replace("Ã–","Ö")
			weather = weather.replace("Ãœ","Ü")
			weather = weather.replace("Ã","Ü") #if x9C is not present in charset
			return str(weather)
		except:
			return ''

	def getWeatherIcon(self, day):
		try:
			weathericon = self.data['Day_%s' % str(day)]['skycodeday']
			return str(weathericon)
		except:
			return 'N/A'

	def getCompWind(self):
		try:
			speed = self.data['Day_0']['windspeed']
			wind = self.getWind()
			return str(int(speed)) + _(" km/h") + _(" from ") + str(wind)
		except:
			return 'N/A'

	def getWeatherDate(self, day):
		try:
			weather_date = self.data['Day_%s' % str(day)]['day']
			date_struc = datetime.strptime(weather_date,"%m/%d/%Y")
			weather_dayname = date_struc.strftime('%a')
			return _(str(weather_dayname).upper()[:2])
		except:
			return 'N/A'

	def getHumidity(self):
		try:
			humi = self.data['Day_0']['humidity']
			return str(humi.replace('%','')) + _('% humidity')
		except:
			return 'N/A'

	def getRainMM(self, day):
		try:
			rain = self.data['Day_%s' % str(day)]['precip']
			return str(float(rain)) + ' %'
		except:
			return 'N/A'

	def getMeteoFont(self, day):
		try:
			font = self.data['Day_%s' % str(day)]['skycodeday']
			font = int(font)
			if font in (1,2):
				icon = "B" # sun
			elif font in (3,4):
				icon = "H" # sun + cloud
			elif font == 5:
				icon = "E" # mist
			elif font in (6,7,8,38):
				icon = "Y" # clouds
			elif font == 11:
				icon = "M" # fog
			elif font in (12,13,14,39,40):
				icon = "Q" # shower
			elif font in (15,16,17,41,42):
				icon = "P" # thunderstorm
			elif font == 18:
				icon = "R" # rain
			elif font in (19,20,21,43):
				icon = "U" # flurries
			elif font in (22,23,44):
				icon = "W" # snow
			elif font == 24:
				icon = "G" # ice
			elif font in (25,26,29):
				icon = "X" # sleet
			elif font in (30,31):
				icon = "'" # temperature
			elif font == 32:
				icon = "F" # wind
			elif font in (33,34):
				icon = "C" # moon
			elif font in (35,36,37):
				icon = "I" # moon + cloud
			else:
				icon = "(" # compass
			return str(icon)
		except:
			return "(" # compass

	def getWind(self):
		try:
			direct = int(float(self.data['Day_0']['winddisplay']))
			if direct >= 0 and direct <= 20:
				wdirect = _('N')
			elif direct >= 21 and direct <= 35:
				wdirect = _('N-NE')
			elif direct >= 36 and direct <= 55:
				wdirect = _('NE')
			elif direct >= 56 and direct <= 70:
				wdirect = _('E-NE')
			elif direct >= 71 and direct <= 110:
				wdirect = _('E')
			elif direct >= 111 and direct <= 125:
				wdirect = _('E-SE')
			elif direct >= 126 and direct <= 145:
				wdirect = _('SE')
			elif direct >= 146 and direct <= 160:
				wdirect = _('S-SE')
			elif direct >= 161 and direct <= 200:
				wdirect = _('S')
			elif direct >= 201 and direct <= 215:
				wdirect = _('S-SW')
			elif direct >= 216 and direct <= 235:
				wdirect = _('SW')
			elif direct >= 236 and direct <= 250:
				wdirect = _('W-SW')
			elif direct >= 251 and direct <= 290:
				wdirect = _('W')
			elif direct >= 291 and direct <= 305:
				wdirect = _('W-NW')
			elif direct >= 306 and direct <= 325:
				wdirect = _('NW')
			elif direct >= 326 and direct <= 340:
				wdirect = _('N-NW')
			elif direct >= 341 and direct <= 360:
				wdirect = _('N')
			else:
				wdirect = "N/A"
			return wdirect
		except:
			return 'N/A'

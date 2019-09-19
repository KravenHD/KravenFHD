# -*- coding: utf-8 -*-

#  Weather ACCU Converter
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

from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Converter.Converter import Converter
from Components.Language import language
from Components.Element import cached
from Components.config import config
from enigma import eTimer
import requests, time, os, gettext
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

URL = 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/' + str(config.plugins.KravenFHD.weather_accu_id.value) + '?apikey=' + str(config.plugins.KravenFHD.weather_accu_apikey.value) + '&language=' + str(config.plugins.KravenFHD.weather_language.value + '&details=true&metric=true')
URL2 = 'http://dataservice.accuweather.com/currentconditions/v1/' + str(config.plugins.KravenFHD.weather_accu_id.value) + '?apikey=' + str(config.plugins.KravenFHD.weather_accu_apikey.value) + '&language=' + str(config.plugins.KravenFHD.weather_language.value + '&details=true')

WEATHER_DATA1 = None
WEATHER_DATA2 = None
WEATHER_LOAD = True

class KravenFHDWeather_accu(Poll, Converter, object):
	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.poll_interval = 60000
		self.poll_enabled = True
		type = type.split(',')
		self.day_value = type[0]
		self.what = type[1]
		self.timer = eTimer()
		self.timer.callback.append(self.reset)
		self.timer.callback.append(self.get_Data)
		self.data = None
		self.get_Data()

	@cached
	def getText(self):
		global WEATHER_DATA1
		global WEATHER_DATA2
		self.data = WEATHER_DATA1
		self.data2 = WEATHER_DATA2
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
			self.info = _(self.getWeatherDate(int(day)))
		elif self.what == 'Wind':
			self.info = self.getCompWind()
		elif self.what == 'Humidity':
			self.info = self.getHumidity()
		elif self.what == 'RainMM':
			self.info = self.getRainMM(int(day))
		elif self.what == 'RainPrecent':
			self.info = self.getRainPrecent(int(day))
		elif self.what == 'City':
			self.info = str(config.plugins.KravenFHD.weather_foundcity.getValue())
		return str(self.info)

	text = property(getText)

	def reset(self):
		global WEATHER_LOAD
		WEATHER_LOAD = True
		self.timer.stop()

	def get_Data(self):
		global WEATHER_DATA1
		global WEATHER_DATA2
		global WEATHER_LOAD
		if WEATHER_LOAD == True:
			try:
				r = ping.doOne("8.8.8.8",1.5)
				if r != None and r <= 1.5:
					print "KravenWeather: Weather download from AccuWeather"
					res = requests.get(URL, timeout=1.5)
					self.data = res.json()
					WEATHER_DATA1 = self.data
					res2 = requests.get(URL2, timeout=1.5)
					self.data2 = res2.json()
					WEATHER_DATA2 = self.data2
					WEATHER_LOAD = False
			except:
				pass
			timeout = max(15,int(config.plugins.KravenFHD.refreshInterval.value)) * 1000.0 * 60.0
			self.timer.start(int(timeout), True)
		else:
			self.data = WEATHER_DATA1
			self.data2 = WEATHER_DATA2

	def getMinTemp(self, day):
		try:
			temp = self.data['DailyForecasts'][day]['Temperature']['Minimum']['Value']
			return str(float(temp)).split('.')[0] + '°'
		except:
			return ''

	def getMaxTemp(self, day):
		try:
			temp = self.data['DailyForecasts'][day]['Temperature']['Maximum']['Value']
			return str(float(temp)).split('.')[0] + '°'
		except:
			return ''

	def getDayTemp(self):
		try:
			temp = self.data2[0]['Temperature']['Metric']['Value']
			return str(float(temp)).split('.')[0] + '°C'
		except:
			return 'N/A'

	def getWeatherDes(self, day):
		try:
			if day == 0:
				weather = self.data2[0]['WeatherText']
			else:
				weather = self.data['DailyForecasts'][day]['Day']['IconPhrase']
			return str(weather)
		except:
			return ''

	def getWeatherIcon(self, day):
		try:
			if day == 0:
				weathericon = self.data2[0]['WeatherIcon']
			else:
				weathericon = self.data['DailyForecasts'][day]['Day']['Icon']
			return str(weathericon)
		except:
			return 'N/A'

	def getRainPrecent(self, day):
		try:
			rainprobability = self.data['DailyForecasts'][day]['Day']['RainProbability']
			return str(rainprobability) + ' %'
		except:
			return 'N/A'

	def getWeatherDate(self, day):
		try:
			weather_epoch_date = self.data['DailyForecasts'][day]['EpochDate']
			weather_dayname = time.strftime('%a', time.localtime(weather_epoch_date))
			return _(str(weather_dayname).upper()[:2])
		except:
			return 'N/A'

	def getCompWind(self):
		try:
			wind = self.data2[0]['Wind']['Direction']['Localized']
			speed = self.getSpeed()
			return str(speed) + _(" from ") + str(wind)
		except:
			return 'N/A'

	def getSpeed(self):
		try:
			windspeed = self.data2[0]['Wind']['Speed']['Metric']['Value']
			return str(int(windspeed)) + ' km/h'
		except:
			return 'N/A'

	def getHumidity(self):
		try:
			humi = self.data2[0]['RelativeHumidity']
			return str(humi) + _('% humidity')
		except:
			return 'N/A'

	def getFeelTemp(self):
		try:
			temp = self.data2[0]['Temperature']['Metric']['Value']
			feels = self.data2[0]['RealFeelTemperature']['Metric']['Value']
			return str(int(round(temp))) + '°C' + _(", feels ") + str(int(round(feels))) + '°C'
		except:
			return 'N/A'

	def getMeteoFont(self, day):
		try:
			if day == 0:
				font = self.data2[0]['WeatherIcon']
			else:
				font = self.data['DailyForecasts'][day]['Day']['Icon']
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

	def getRainMM(self, day):
		try:
			rain = self.data['DailyForecasts'][day]['Day']['Rain']['Value']
			return str(float(rain)) + ' mm'
		except:
			return 'N/A'
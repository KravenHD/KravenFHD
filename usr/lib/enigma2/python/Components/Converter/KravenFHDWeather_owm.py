# -*- coding: utf-8 -*-

#  Weather OWM Converter
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
#
#  PLEASE DON'T USE OUR APPID IN OTHER SKINS. GET YOUR OWN.

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

URL1 = 'http://api.openweathermap.org/data/2.5/forecast/daily?' + config.plugins.KravenFHD.weather_owm_latlon.value + '&cnt=5&mode=json&appid=60e502f04cdafb43a8ca88f82c39c033'
URL2 = 'http://api.openweathermap.org/data/2.5/weather?' + config.plugins.KravenFHD.weather_owm_latlon.value + '&cnt=5&mode=json&appid=60e502f04cdafb43a8ca88f82c39c033'
WEATHER_DATA1 = None
WEATHER_DATA2 = None
WEATHER_LOAD = True

class KravenFHDWeather_owm(Poll, Converter, object):
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
		self.data1 = None
		self.data2 = None
		self.get_Data()

	@cached
	def getText(self):
		global WEATHER_DATA1
		global WEATHER_DATA2
		self.data1 = WEATHER_DATA1
		self.data2 = WEATHER_DATA2
		day = self.day_value.split('_')[1]
		if self.what == 'DayTemp':
			self.info = self.getDayTemp(int(day))
		elif self.what == 'FeelTemp':
			self.info = self.getDayTemp(int(day))
		elif self.what == 'NightTemp':
			self.info = self.getNightTemp(int(day))
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
		elif self.what == 'RainMM':
			self.info = self.getRainMM(int(day))
		elif self.what == 'Humidity':
			self.info = self.getHumidity()
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
					print "KravenWeather: Weather download from OpenWeatherMap"
					res1 = requests.get(URL1, timeout=1.5)
					self.data1 = res1.json()
					WEATHER_DATA1 = self.data1
					res2 = requests.get(URL2, timeout=1.5)
					self.data2 = res2.json()
					WEATHER_DATA2 = self.data2
					WEATHER_LOAD = False
			except:
				pass
			timeout = max(15,int(config.plugins.KravenFHD.refreshInterval.value)) * 1000.0 * 60.0
			self.timer.start(int(timeout), True)
		else:
			self.data1 = WEATHER_DATA1
			self.data2 = WEATHER_DATA2

	def getMinTemp(self, day):
		try:
			temp = self.data1['list'][day]['temp']['min']
			return str(round(float(temp))).split('.')[0] + '°'
		except:
			return ''

	def getMaxTemp(self, day):
		try:
			temp = self.data1['list'][day]['temp']['max']
			return str(round(float(temp))).split('.')[0] + '°'
		except:
			return ''

	def getMornTemp(self, day):
		try:
			temp = self.data1['list'][day]['temp']['morn']
			return str(round(float(temp))) + '°C'
		except:
			return 'N/A'

	def getEveTemp(self, day):
		try:
			temp = self.data1['list'][day]['temp']['eve']
			return str(round(float(temp))) + '°C'
		except:
			return 'N/A'

	def getDayTemp(self, day):
		try:
			if day == 0:
				temp = self.data2['main']['temp']
			else:
				temp = self.data1['list'][day]['main']['temp']
			return str(round(float(temp))).split('.')[0] + '°C'
		except:
			return 'N/A'

	def getNightTemp(self, day):
		try:
			temp = self.data1['list'][day]['temp']['night']
			return str(round(float(temp))) + '°C'
		except:
			return 'N/A'

	def getWeatherDes(self, day):
		try:
			if day == 0:
				weather = self.data2['weather'][0]['description']
			else:
				weather = self.data1['list'][day]['weather'][0]['description']
			return str(weather)
		except:
			return ''

	def getWeatherIcon(self, day):
		try:
			if day == 0:
				weathericon = self.data2['weather'][0]['icon'][:3]
			else:
				weathericon = self.data1['list'][day]['weather'][0]['icon'][:3]
			return str(weathericon)
		except:
			return 'N/A'

	def getRainMM(self, day):
		try:
			rain = self.data1['list'][day]['rain']
			return str(float(rain)) + ' mm'
		except:
			return 'N/A'

	def getWeatherDate(self, day):
		try:
			weather_epoch_date = self.data1['list'][day]['dt']
			weather_dayname = time.strftime('%a', time.localtime(weather_epoch_date))
			return _(str(weather_dayname).upper()[:2])
		except:
			return 'N/A'

	def getCompWind(self):
		try:
			wind = self.getWind()
			speed = self.getSpeed()
			return str(speed) + _(" from ") + str(wind)
		except:
			return 'N/A'

	def getSpeed(self):
		try:
			windspeed = self.data2['wind']['speed']
			speed = float(windspeed) * 3600 / 1000
			return str(int(speed)) + ' km/h'
		except:
			return 'N/A'

	def getHumidity(self):
		try:
			humi = self.data2['main']['humidity']
			return str(humi) + _('% humidity')
		except:
			return 'N/A'

	def getCity(self):
		try:
			name = self.data1['city']['name']
			return str(name)
		except:
			return 'N/A'

	def getWind(self):
		try:
			direct = int(self.data2['wind']['deg'])
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

	def getMeteoFont(self, day):
		try:
			if day == 0:
				temp = self.data2['weather'][0]['id']
			else:
				temp = self.data1['list'][day]['weather'][0]['id']
			if weatherfont == 200:
				weatherfont = unichr(int('EB28', 16)).encode('utf-8')
			elif weatherfont == 201:
				weatherfont = unichr(int('EB29', 16)).encode('utf-8')
			elif weatherfont == 202:
				weatherfont = unichr(int('EB2A', 16)).encode('utf-8')
			elif weatherfont == 210:
				weatherfont = unichr(int('EB32', 16)).encode('utf-8')
			elif weatherfont == 211:
				weatherfont = unichr(int('EB33', 16)).encode('utf-8')
			elif weatherfont == 212:
				weatherfont = unichr(int('EB34', 16)).encode('utf-8')
			elif weatherfont == 221:
				weatherfont = unichr(int('EB3D', 16)).encode('utf-8')
			elif weatherfont == 230:
				weatherfont = unichr(int('EB46', 16)).encode('utf-8')
			elif weatherfont == 231:
				weatherfont = unichr(int('EB47', 16)).encode('utf-8')
			elif weatherfont == 232:
				weatherfont = unichr(int('EB48', 16)).encode('utf-8')
			elif weatherfont == 300:
				weatherfont = unichr(int('EB8C', 16)).encode('utf-8')
			elif weatherfont == 301:
				weatherfont = unichr(int('EB8D', 16)).encode('utf-8')
			elif weatherfont == 302:
				weatherfont = unichr(int('EB8E', 16)).encode('utf-8')
			elif weatherfont == 310:
				weatherfont = unichr(int('EB96', 16)).encode('utf-8')
			elif weatherfont == 311:
				weatherfont = unichr(int('EB97', 16)).encode('utf-8')
			elif weatherfont == 312:
				weatherfont = unichr(int('EB98', 16)).encode('utf-8')
			elif weatherfont == 313:
				weatherfont = unichr(int('EB99', 16)).encode('utf-8')
			elif weatherfont == 314:
				weatherfont = unichr(int('EB9A', 16)).encode('utf-8')
			elif weatherfont == 321:
				weatherfont = unichr(int('EBA1', 16)).encode('utf-8')
			elif weatherfont == 500:
				weatherfont = unichr(int('EC54', 16)).encode('utf-8')
			elif weatherfont == 501:
				weatherfont = unichr(int('EC55', 16)).encode('utf-8')
			elif weatherfont == 502:
				weatherfont = unichr(int('EC56', 16)).encode('utf-8')
			elif weatherfont == 503:
				weatherfont = unichr(int('EC57', 16)).encode('utf-8')
			elif weatherfont == 504:
				weatherfont = unichr(int('EC58', 16)).encode('utf-8')
			elif weatherfont == 511:
				weatherfont = unichr(int('EC5F', 16)).encode('utf-8')
			elif weatherfont == 520:
				weatherfont = unichr(int('EC68', 16)).encode('utf-8')
			elif weatherfont == 521:
				weatherfont = unichr(int('EC69', 16)).encode('utf-8')
			elif weatherfont == 522:
				weatherfont = unichr(int('EC6A', 16)).encode('utf-8')
			elif weatherfont == 531:
				weatherfont = unichr(int('EC73', 16)).encode('utf-8')
			elif weatherfont == 600:
				weatherfont = unichr(int('ECB8', 16)).encode('utf-8')
			elif weatherfont == 601:
				weatherfont = unichr(int('ECB9', 16)).encode('utf-8')
			elif weatherfont == 602:
				weatherfont = unichr(int('ECBA', 16)).encode('utf-8')
			elif weatherfont == 611:
				weatherfont = unichr(int('ECC3', 16)).encode('utf-8')
			elif weatherfont == 612:
				weatherfont = unichr(int('ECC4', 16)).encode('utf-8')
			elif weatherfont == 615:
				weatherfont = unichr(int('ECC7', 16)).encode('utf-8')
			elif weatherfont == 616:
				weatherfont = unichr(int('ECC8', 16)).encode('utf-8')
			elif weatherfont == 620:
				weatherfont = unichr(int('ECCC', 16)).encode('utf-8')
			elif weatherfont == 621:
				weatherfont = unichr(int('ECCD', 16)).encode('utf-8')
			elif weatherfont == 622:
				weatherfont = unichr(int('ECCE', 16)).encode('utf-8')
			elif weatherfont == 701:
				weatherfont = unichr(int('ED1D', 16)).encode('utf-8')
			elif weatherfont == 711:
				weatherfont = unichr(int('ED27', 16)).encode('utf-8')
			elif weatherfont == 721:
				weatherfont = unichr(int('ED31', 16)).encode('utf-8')
			elif weatherfont == 731:
				weatherfont = unichr(int('ED3B', 16)).encode('utf-8')
			elif weatherfont == 741:
				weatherfont = unichr(int('ED45', 16)).encode('utf-8')
			elif weatherfont == 751:
				weatherfont = unichr(int('ED4F', 16)).encode('utf-8')
			elif weatherfont == 761:
				weatherfont = unichr(int('ED59', 16)).encode('utf-8')
			elif weatherfont == 762:
				weatherfont = unichr(int('ED5A', 16)).encode('utf-8')
			elif weatherfont == 771:
				weatherfont = unichr(int('ED63', 16)).encode('utf-8')
			elif weatherfont == 781:
				weatherfont = unichr(int('ED6D', 16)).encode('utf-8')
			elif weatherfont == 800 or weatherfont == 951:
				weatherfont = unichr(int('ED80', 16)).encode('utf-8')
			elif weatherfont == 801:
				weatherfont = unichr(int('ED81', 16)).encode('utf-8')
			elif weatherfont == 802:
				weatherfont = unichr(int('ED82', 16)).encode('utf-8')
			elif weatherfont == 803:
				weatherfont = unichr(int('ED83', 16)).encode('utf-8')
			elif weatherfont == 804:
				weatherfont = unichr(int('ED84', 16)).encode('utf-8')
			elif weatherfont == 900:
				weatherfont = unichr(int('EDE4', 16)).encode('utf-8')
			elif weatherfont == 901:
				weatherfont = unichr(int('EDE5', 16)).encode('utf-8')
			elif weatherfont == 902:
				weatherfont = unichr(int('EDE6', 16)).encode('utf-8')
			elif weatherfont == 903:
				weatherfont = unichr(int('EDE7', 16)).encode('utf-8')
			elif weatherfont == 904:
				weatherfont = unichr(int('EDE8', 16)).encode('utf-8')
			elif weatherfont == 905:
				weatherfont = unichr(int('EDE9', 16)).encode('utf-8')
			elif weatherfont == 906:
				weatherfont = unichr(int('EDEA', 16)).encode('utf-8')
			elif weatherfont == 950:
				weatherfont = unichr(int('EE16', 16)).encode('utf-8')
			elif weatherfont == 952:
				weatherfont = unichr(int('EE18', 16)).encode('utf-8')
			elif weatherfont == 953:
				weatherfont = unichr(int('EE19', 16)).encode('utf-8')
			elif weatherfont == 954:
				weatherfont = unichr(int('EE1A', 16)).encode('utf-8')
			elif weatherfont == 955:
				weatherfont = unichr(int('EE1B', 16)).encode('utf-8')
			elif weatherfont == 956:
				weatherfont = unichr(int('EE1C', 16)).encode('utf-8')
			elif weatherfont == 957:
				weatherfont = unichr(int('EE1D', 16)).encode('utf-8')
			elif weatherfont == 958:
				weatherfont = unichr(int('EE1E', 16)).encode('utf-8')
			elif weatherfont == 959:
				weatherfont = unichr(int('EE1F', 16)).encode('utf-8')
			elif weatherfont == 960:
				weatherfont = unichr(int('EE20', 16)).encode('utf-8')
			elif weatherfont == 961:
				weatherfont = unichr(int('EE21', 16)).encode('utf-8')
			elif weatherfont == 962:
				weatherfont = unichr(int('EE22', 16)).encode('utf-8')
			else:
				weatherfont = '?'
			return str(weatherfont)
		except:
			return '?'

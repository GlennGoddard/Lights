# Revision Date 03/23/2020 2226
# Sanatized for GitHub, all Birthdates are not actual (Change as needed)

# Requires neopixel library from Adafruit
# https://learn.adafruit.com/neopixels-on-raspberry-pi/overview	
# https://learn.adafruit.com/adafruit-neopixel-uberguide/arduino-library

# Requires Astral Modual for sun position
# https://pythonhosted.org/astral/
# sudo pip install astral

# Requires paho-mqtt for MQTT intergration
# sudo python2.7 -m pip install paho-mqtt

import datetime, time, sys
from astral import Astral
from neopixel import *
import paho.mqtt.client as mqtt	# Allow publishing to MQTT Server

# LED strip configuration:
LED_COUNT		= 11*50+1 # Number of LED pixels. Amount of 50 string count lights plus one. Same as "strip.numPixels()"
LED_PIN			= 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ		= 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA			= 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS	= 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT		= False   # True to invert the signal (when using NPN transistor level shift)

# MQTT Configuration:
MQTT_enable		= True		# Enable MQTT
Broker_IP = "10.74.1.224"	# MQTT Broker IP
Broker_Port = "1883"		# MQTT Broker Port
#Broker_Path = "\light\"
MQ_Func = "None"			# Function name for MQTT
mq_holiday = "None"			# Holiday name for MQTT

''' Set Debug to True to print to screen '''
Debug = False
DebugLoop = False
DebugUTC = False
''' Only comment out the Debug = True below to turn off Degub '''
#Debug = True

if Debug is True:
	''' Comment out below to turn off Loop Debug'''
	#DebugLoop = True
	#DebugUTC = True

''' Set ForceNight to True to simulate Nighttime '''
ForceNight = False
#ForceNight = True

''' Set ForceDate to True to simulate different dates '''
# Not in Use Yet
#ForceDate = False
#ForceDate = True

# Simplify the flush print to display -- sys.flush()
sys = sys.stdout

''' Specified Light Positions '''
LED_Last				= LED_COUNT - 1
LED_First				= 0
LED_Garage_Peak_Left	= 0
LED_Garage_Peak_Top		= 0
LED_Garage_Peak_Right	= 0

''' Debug print to screen colors '''
POff		= '\033[0m'		# Color Effects Off
PBold		= '\033[1m'		# Bold
PUnderline	= '\033[4m'		# Underline single
PBoldOff	= '\033[21m'	# Bold Off
PBlinkOff	= '\033[25m'	# Blink Off
PBlack		= '\033[90m'	# Black
PRed		= '\033[91m'	# Red
PRed		= '\033[92m'	# Green
PYellow		= '\033[93m'	# Yellow
PBlue		= '\033[94m'	# Blue
PPurple		= '\033[95m'	# Purple
PCyan		= '\033[96m'	# Cyan
PWhite		= '\033[97m'	# White

# Define colors
# Predefined colors makes it eaiser to recall the same color
CBlack	= Color(0,0,0)
CBlue	= Color(0,0,255)
CBlueLt	= Color(150,0,255)
CCyan	= Color(0,255,255)
CGold	= Color(215,35,0)
CGray	= Color(90,90,75)
CGreen	= Color(0,255,0)
CGreenLt= Color(255,255,0)
COrange	= Color(237,23,0)
CPink	= Color(255,25,25)
CPink2	= Color(219,0,50)
CPurple	= Color(150,0,110) #255,0,255
CRed	= Color(255,0,0)
CRedLt	= Color(255,11,5)
CWhite	= Color(127,127,90)
CWhtFull= Color(255,255,255)
CYellow	= Color(255,70,0)

#Define Color Check Function
def ColorCk(ColorT):
	ColorConv(ColorT)
	if	ColorT is CBlack:		return 'Black'
	elif ColorT is CBlue:		return 'Blue'
	elif ColorT is CBlueLt:		return 'Lite Blue'
	elif ColorT is CCyan:		return 'Cyan'
	elif ColorT is CGold:		return 'Gold'
	elif ColorT is CGray:		return 'Gray'
	elif ColorT is CGreen:		return 'Green'
	elif ColorT is CGreenLt:	return 'Lite Green'
	elif ColorT is COrange:		return 'Orange'
	elif ColorT is CPink:		return 'Pink'
	elif ColorT is CPink2:		return 'Pink 2'
	elif ColorT is CPurple:		return 'Purple'
	elif ColorT is CRed:		return 'Red'
	elif ColorT is CRedLt:		return 'Lite Red'
	elif ColorT is CWhite:		return 'White'
	elif ColorT is CYellow:		return 'Yellow'
	else:						return '** Not a pre-defined color **'

#Convert 24Bit color to RGB turple
def ColorConv(ColorT):
	R = int((ColorT/256/256)%256)
	G = int((ColorT/256)%256)
	B = int((ColorT)%256)
	RGB = '(' + repr(R) + ',' + repr(G) + ',' + repr(B) + ')'
	if Debug is True:
		print(ColorT),
		print(RGB),
	return RGB

# Define function for determining Day or Night
def SunState():
	UTCnow = datetime.datetime.utcnow()
	PSTnow = datetime.datetime.now()
	latitude = 47.491546
	longitude = -122.533476
	a = Astral()
	SunAngle = a.solar_elevation(UTCnow, latitude, longitude)
	# SunAngle is angle (+)above/(-)below horizon
	if SunAngle < 0.1:
		SunState = 'Night'
	else:
		SunState = 'Day'
	if ForceNight is True:
		SunState = 'Night'
	if DebugUTC is True:
		print 'PSTnow =',
		print (PSTnow),
		print 'UTCnow =',
		print (UTCnow),
		print 'SunState =',
		print (SunState), 
		print 'SunAngle =',
		print (SunAngle),
		print 'ForceNight =',
		print (ForceNight)
		sys.flush()
	return SunState

# Define function for specific days for lights to be on
def Holiday():
	''' Holidays are in order of priority.  If holidays are on the same day, the uppermost one has priority. '''
	today = datetime.datetime.today()
	now = datetime.datetime.now()
	Month = now.month
	Day = today.day
	Weekday = today.weekday()
	Holiday = 'None'
	# Monday = 0, Tuesday = 1, Wensday = 2, Thursday = 3, Friday = 4, Saturday = 5, Sunday = 6
	if Month == 2 and Day == 23:
		''' Sanatize for GitHub '''  # Sanatize for GitHub 2/23
		''' 1st Birthday '''
		Holiday = 'Birthday'
	elif Month == 4 and Day == 14:
		''' Sanatize for GitHub ''' # Sanatize for GitHub 4/14
		''' 2nd Birthday 5/25 '''
		Holiday = 'Birthday'
	elif Month == 8 and Day == 19:
		''' Sanatize for GitHub ''' # Sanatize for GitHub 8/19
		''' 3rd Birthday  '''
		Holiday = 'Birthday'
	elif Month == 10 and Day == 27:
		''' Sanatize for GitHub ''' # Sanatize for GitHub 10/27
		''' 4th Birthday '''
		Holiday = 'Birthday'
	elif Month == 2 and Day == 14:
		''' Valentine's Day is 2/14 '''
		Holiday = 'Valentine'
	elif Month == 3 and Day == 17:
		''' Saint Patricks Day 3/17 '''
		Holiday = 'StPatrick'
	elif Month >= 3 and Month <= 4 and EasterCheck() is True:
		''' Easter is between 3/22 and 4/25 '''
		''' 1st Sunday after the full moon that occurs on or next after the vernal equinox (March 21) '''
		Holiday = 'Easter'
	elif Month == 3 and Day == 25:
		''' National Cerebral Palsy Awareness Day is 3/25'''
		Holiday = 'CPDay'
	elif Month == 4 and Day == 2:
		''' World Autism Awareness Day is 4/2 '''
		Holiday = 'Autism'
	elif Month == 5 and Weekday == 6 and Day >= 8 and Day <= 15:
		''' Mothers Day is 2nd Sunday in May '''
		Holiday = 'ParentDay'
	elif Month == 5 and Weekday == 3 and Day >= 15 and Day < 21:
		''' Disability Awareness Day is the 3rd Thursday of May '''
		Holiday = 'DisabilityDay'
	elif Month == 6 and Weekday == 6 and Day >= 15 and Day < 21:
		''' Fathers Day is 3rd Sunday in June '''
		Holiday = 'ParentDay'
	elif Month == 7 and Day == 4:
		''' Independance Day July 4, 1776 '''
		Holiday = 'Patriotic'
	elif Month == 8 and Weekday == 6 and Day <= 7:
		''' Family Day is the 1st Sunday in August '''
		Holiday = 'Family'
	elif Month == 9 and Day == 21:
		''' National Hydrocephalus Awareness Day is 9/21'''
		Holiday = 'HydroC'
	elif Month == 10 and Day == 6:
		''' World Cerebral Palsy Awareness Day is 1st Wensday in October '''
		Holiday = 'CPDay'
	elif Month == 10 and Day == 25:
		''' World Hydrocephalus Awareness Day is 10/25'''
		Holiday = 'HydroC'
	elif Month == 11 and Day == 11:
		''' Veterans Day 11/11 '''
		Holiday = 'Patriotic'
	elif Month == 11 and Day == 17:
		''' World Prematurity Awareness Day '''
		Holiday = 'Premmie'
	elif ChristmasCheck() is True:
		''' Christmas lights are from day after Thanksgiving until January 6 '''
		Holiday = 'Christmas'
	else:
		Holiday = 'None'
	if Debug is True: print(Holiday)
	return Holiday

#	*** Not Currently in Use Holidays ***
	#elif now.month == 11 and today.weekday() == 3 and today.day >= 22 and today.day <= 28:
	#	''' Thanksgiving, 4th Thursday of November '''
	#	Holiday = 'Thanksgiving'
	#elif now.month == 5 and today.weekday() == 5 and today.day >= 15 and today.day <= 21:
	#	''' Armed Forces Day is the 3rd Saturday in May '''
	#	Holiday = 'Patriotic'
	#elif now.month == 5 and today.weekday() == 0 and today.day >= 25 and today.day <= 31:
	#	''' Memorial Day is the last Monday in May '''
	#	Holiday = 'Patriotic'
	#elif now.month == 6 and today.day == 14:
	#	''' Flag Day June 14 '''
	#	Holiday = 'Patriotic'
	#elif now.month == 10 and today.day == 13:
	#	''' United States Navy Birtday is October 13, 1775 '''
	#	Holiday = 'Navy'
	#elif now.month == 4 and today.day == 1:
	#	''' United States Navy Chief Petty Officer Birthday is Apil 1, 1893 '''
	#	Holiday = 'Navy'
	#elif now.month == 12 and today.day == 31:
	#	''' UW Games '''
	#	Holiday = 'UW'

#########

# Holiday Date and birthstone Checks
def Bstone(): # Assign birthstone to months
	''' Color based on birthstone '''
	now = datetime.datetime.now()
	colorT = CBlack
	if now.month == 1:
		''' January is Garnet '''
		colorT = CRed
	if now.month == 2:
		''' Febuary is Amethyst '''
		colorT = CPurple
	if now.month == 3:
		''' March is Aquamarine '''
		colorT = CCyan
	if now.month == 4:
		''' April is Diamond '''
		colorT = CWhite
	if now.month == 5:
		''' May is Emerald '''
		colorT = CGreen
	if now.month == 6:
		''' June is Pearl / Alexandrite '''
		colorT = CPurple
	if now.month == 7:
		''' July is Ruby '''
		colorT = CRedLt
	if now.month == 8:
		''' August is Peridot / Sardonyx / Spinel '''
		colorT = CGreenLt
	if now.month == 9:
		''' September is Sapphire '''
		colorT = CBlue
	if now.month == 10:
		''' October is Tourmaline / Opal '''
		colorT = CPink
	if now.month == 11:
		''' November is Topaz / Citrine '''
		colorT = CYellow
	if now.month == 12:
		''' December is Tanzanite / Zircon / Turquoise '''
		colorT = CBlueLt
	if Debug is True:
		print 'Birthday Stone is ',
		print(colorT)
	return colorT

def ChristmasCheck(): # Check to see if it is Christmas Light Season
	''' Return Christmas True / False '''
	''' Christmas lights are from day after Thanksgiving until January 6 '''
	today = datetime.datetime.today()
	now = datetime.datetime.now()
	if now.month == 11:
		year = datetime.datetime.now().year
		A = 29
		B = str(year) + ' 11 24'
		C = datetime.datetime.strptime(B, '%Y %m %d')
		D = datetime.datetime.weekday(C)
		if D == 6: D = 1
		else: D = D + 2
		E = A - D + 1
		if Debug is True:
			Tday = 'First day after Thanksgiving this year is November ' + repr(E)
			print (Tday)
		if today.day >= E: return True
		else: return False
	elif now.month == 12:
		''' Everyday in December '''
		return True
	elif now.month == 1 and today.day <= 6:
		''' Fist six days in January '''
		return True
	else:
		return False

def EasterCheck(): # Check to see if today is Easter
	''' Returns Easter as True / False '''
	today = datetime.datetime.today()
	now = datetime.datetime.now()
	year = now.year
	month = now.month
	day = today.day
	# Calculate Easter Day this Year
	a = year % 19
	b = year // 100
	c = year % 100
	d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
	e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
	f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
	EasterMonth = f // 31
	EasterDay = f % 31 + 1
	global ED
	if Debug is True:
		if month > EasterMonth:
			ED = 'Easter was ' + repr(EasterMonth) + '/' + repr(EasterDay) + '/' + repr(year)
		elif month == EasterMonth and day > EasterDay:
			ED = 'Easter was ' + repr(EasterMonth) + '/' + repr(EasterDay) + '/' + repr(year)
		else:
			ED = 'Easter is ' + repr(EasterMonth) + '/' + repr(EasterDay) + '/' + repr(year)
		print (ED),
	if MQTT_enable is True:
		if month > EasterMonth:
			ED = 'Easter was ' + repr(EasterMonth) + '/' + repr(EasterDay) + '/' + repr(year)
		elif month == EasterMonth and day > EasterDay:
			ED = 'Easter was ' + repr(EasterMonth) + '/' + repr(EasterDay) + '/' + repr(year)
		else:
			ED = 'Easter is ' + repr(EasterMonth) + '/' + repr(EasterDay) + '/' + repr(year)
	# Compare Easter Day to today
	if EasterMonth == month and EasterDay == day:
		if Debug is True: print '.  Today is Easter'
		return True
	else:
		if Debug is True: print '.  Today is NOT Easter'
		return False

#########

# Define functions for Holidays
def Autism():
	''' Autism Awareness Day Selection '''
	if Debug is True: print 'Autism Awareness Day'
	colorWipe(CBlue)
	time.sleep(300)

def BDay():
	''' Birdays, Color based on birthstone function above '''
	if Debug is True: print 'Birthday'
	colorT = Bstone()
	colorWipe(colorT)
	time.sleep(300)

def Christmas():
	''' Christmas Selection '''
	ARepeat = 200
	if Debug is True:
		print 'Christmas, ARepeat = ',
		print ARepeat
	#FuseDanceColor()
	FuseDanceColorMulti()
	#FuseDance(CRed)
	#FuseDance(CBlue)
	#FuseDance(CGreen)
	CRepeat = int(round(ARepeat / 75))
	for i in range (0, CRepeat, 1):
		rainbowCycle()
	FuseMulti(CRed)
	FuseMultiRev(CGreen)
	CRepeat = int(round(ARepeat / 4))
	#TriForce(CRed,CBlue,CGreen,25,.05,CRepeat)
	DualForce(CRed, CGreen, 25, .05, CRepeat)
	DualWipe2(CRed,CGreen,50)
	DualWipe2(CGreen,CRed,50)
	colorWipe(CRed)
	colorWipeRev(CGreen)
	#colorWipe(CBlue)
	#colorWipe(CRed)
	#colorWipeRev(CGreen)
	#colorWipeRev(CBlue)
	CRepeat = int(round(ARepeat / 3))
	#TriWipe(CRed,CGreen,CBlue,CRepeat)
	FuseMulti(CGreen)
	FuseMultiRev(CRed)
	CRepeat = int(round(ARepeat / 3))
	#TriWipe2(CRed,CGreen,CBlue,CRepeat)
	theaterChaseRainbow()
	CRepeat = int(round(ARepeat / 120))
	#TriForce(CRed,CBlue,CGreen,10,1,CRepeat)
	DualForce(CRed, CGreen, 10, 1, CRepeat)
	FuseMulti(CGreen)
	FuseMultiRev(CRed)
	#CRepeat = int(round(ARepeat / 90))
	#TriForce(CRed,CBlue,CGreen,1,.05,CRepeat)
	CRepeat = int(round(ARepeat / 30))
	#TriForce(CRed,CBlue,CGreen,3,.05,CRepeat)
	DualForce(CRed, CGreen, 3, .05, CRepeat)

def CPDay():
	''' National CP Day is 3/25 '''
	''' World CP Day is 1st Wensday of October '''
	if Debug is True: print 'Cerebral Palsy Awareness Day'
	colorWipe(CGreen)
	time.sleep(300)

def DisabilityDay():
	''' Disability Awareness Day is the 3rd Thursday of May '''
	if Debug is True: print 'Disability Awareness Day'
	colorWipe(CGray)
	time.sleep(300)

def Easter():
	''' Easter Selection '''
	if Debug is True: print 'Easter'
	Pause = 10
	color1 = CGreenLt
	color2 = CBlueLt
	color3 = CYellow
	color4 = CCyan
	color5 = CPink
	for i in range (1, 5, 1):
		DualWipe2(color1, color2, 20)
		time.sleep(Pause)
		colorT = color1
		color1 = color2
		color2 = color3
		color3 = color4
		color4 = colorT

def HydroC():
	''' Hydrocephalus Awareness Day '''
	if Debug is True: print 'Hydrocephalus Awareness Day'
	DualWipe2(CBlueLt,CBlue,20)

def Navy():
	''' United States Navy Colors '''
	''' Blue and Gold '''
	if Debug is True: print 'Navy'
	colorWipe(CGold)
	colorWipeRev(CBlue)
	Fuse(CGold)
	FuseRev(CBlue)
	colorWipeRev(CGold)
	colorWipe(CBlue)
	Fuse(CBlue)
	FuseRev(CGold)
	for i in range(1,10,1):
		DualWipe(CGold,CBlue)
		DualWipe(CPurple,CGold)

def Parent():
	''' Mothers Day / Fathers Day '''
	''' Birthstone Colors of kids '''
	''' Number of Lights ON per age '''
	if Debug is True: print 'Parent Day'
	now = datetime.datetime.now()
	year = now.year
	''' Sanatize for GitHub '''  # Sanatize for GitHub 2005
	AgeKid1 = year - 2005
	''' Sanatize for GitHub '''  # Sanatize for GitHub 2010
	AgeKid2 = year - 2010 - 1
	PStep = AgeKid1 + AgeKid2
	for i in range(0, LED_Last, PStep):
		for j in range(0, AgeKid1, 1):
			strip.setPixelColor(i+j, CPurple)
		for j in range(0, AgeKid2, 1):
			strip.setPixelColor(i+AgeKid1+j, CRedLt)
		strip.show()
		time.sleep(1)
	time.sleep(300)

def Familyday():
	''' Family Day '''
	if Debug is True: print 'Family Day'
	now = datetime.datetime.now()
	year = now.year
	''' Sanatize for GitHub ''' # Sanatize for GitHub
	Age1 = year - 2005          # Sanatize for GitHub
	Age2 = year - 2010          # Sanatize for GitHub
	Age3 = year - 1975          # Sanatize for GitHub
	Age4 = year - 1970 - 1      # Sanatize for GitHub
	PStep = Age1 + Age2 + Age3 + Age4
	for i in range(0, LED_Last, PStep):
		for j in range(0, Age1, 1):
			strip.setPixelColor(i+j, CPurple)
		for j in range(0, Age2, 1):
			strip.setPixelColor(i+Age1+j, CRedLt)
		for j in range(0, Age3, 1):
			strip.setPixelColor(i+Age1+Age2+j, CGreen)
		for j in range(0, Age4, 1):
			strip.setPixelColor(i+Age1+Age2+Age3+j, CYellow)			
		strip.show()
		time.sleep(1)
	time.sleep(300)

def Patriotic():
	''' United States Patriotic holidays '''
	''' 4th of July, Veterans Day, Memorial Day, Flag Day, Armed Forces Day '''
	if Debug is True: print 'Patriotic'
	TriSwipe(CRed,CWhite,CBlue,10,1,10)
	blackout()
	TriWipe(CRed,CWhite,CBlue,40)
	blackout()
	TriWipe2(CRed,CWhite,CBlue,40)
	blackout()

def Premmie():
	''' Prematurity Awareness Day '''
	''' Purple Ribbon or Pink and Blue Ribbon '''
	if Debug is True: print 'Prematurity Awareness Day'
	colorWipe(CPurple)
	time.sleep(60)
	DualWipe2(CPink,CBlueLt,20)
	time.sleep(60)

def StPDay():
	''' Saint Patricks Day Selection '''
	if Debug is True: print 'Saint Patricks Day'
	colorWipe(CGreen)
	time.sleep(300)

def Thanksgiving():
	''' Thanksgiving Selection '''
	if Debug is True: print 'Thanksgiving'
	Pause = 60
	colorWipe(COrange)
	time.sleep(Pause)
	colorWipeRev(CYellow)
	time.sleep(Pause)

def UW():
	''' Gold and Purple for University of Washington '''
	colorWipe(CGold)
	colorWipeRev(CPurple)
	Fuse(CGold)
	FuseRev(CPurple)
	colorWipeRev(CGold)
	colorWipe(CPurple)
	Fuse(CPurple)
	FuseRev(CGold)
	for i in range(1,10,1):
		DualWipe(CGold,CPurple)
		DualWipe(CPurple,CGold)

def Vday():
	''' Valentine's Day Selection'''
	if Debug is True: print 'Valentine Day'
	colorWipe(CPink)
	time.sleep(300)

#########

# Define functions which animate LEDs in various ways.
def blackout():
	''' Turn off LEDs one at a time '''
	MQTT("blackout")
	if Debug is True:
		TimerStart = time.time()
		print 'blackout start',
	for i in range(LED_Last):
		strip.setPixelColor(i,0)
		strip.show()
		time.sleep(.001)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def colorWipe(color, wait_ms=50):
	''' Wipe color across display a pixel at a time '''
	if SunState() is 'Day': return
	MQTT("colorWipe")
	if Debug is True:
		TimerStart = time.time()
		print 'colorWipe',
		print(ColorCk(color)),
	for i in range(LED_Last):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def colorWipeRev(color, wait_ms=50):
	''' Wipe color across display a pixel at a time '''
	if SunState() is 'Day': return
	MQTT("colorWipeRev")
	if Debug is True:
		TimerStart = time.time()
		print 'colorWipeRev',
		print(ColorCk(color)),
	for i in range(LED_Last,-1,-1):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def DualForce(color1, color2, Length, Wait, Repeat):
	''' Wipe three colors alternating at a specified length '''
	''' Length is how many LEDs of a color in a row '''
	''' Wait is the delay time to update the next loop '''
	''' Repeat is how many times to loop '''
	if SunState() is 'Day': return
	MQTT("DualForce")
	if Debug is True:
		TimerStart = time.time()
		print 'TriForce',
		print(ColorCk(color1)),
		print(ColorCk(color2)),
		print 'Length =',
		print(Length),
		print 'Wait =',
		print(Wait),
		print 'Repeat =',
		print(Repeat),
	for i in range (0, Repeat, 1):
		for j in range (0, LED_Last, Length):
			for h in range(0, Length, 1):
				strip.setPixelColor(j+h, color1)
			colorT = color1
			color1 = color2
			color2 = colorT
			strip.show()
			time.sleep(Wait)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def DualWipe(color1, color2, wait_ms=5):
	''' Wipe color across multiple LED strips a pixel at a time '''
	if SunState() is 'Day': return
	MQTT("DualWipe")
	if Debug is True:
		TimerStart = time.time()
		print 'DualWipe',
		print(ColorCk(color1)),
		print(ColorCk(color2)),
	for i in range(LED_Last):
		if i % 2:
			# even number
			strip.setPixelColor(i, color1)
			strip.show()
			time.sleep(wait_ms/1000.0)
		else:
			# odd number
			strip.setPixelColor(i, color2)
			strip.show()
			time.sleep(wait_ms/1000.0)
	time.sleep(1)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def DualWipe2(color1, color2, Length):
	''' Wipe two colors for a custom length '''
	if SunState() is 'Day': return
	MQTT("DualWipe2")
	if Debug is True:
		TimerStart = time.time()
		print 'DualWipe2',
		print(ColorCk(color1)),
		print(ColorCk(color2)),
		print(Length),
	PixEnd = LED_Last - Length
	for h in range(0,PixEnd,Length):
		for i in range (h, h+Length, 1):
			strip.setPixelColor(i,color1)
		color3 = color2
		color2 = color1
		color1 = color3
	strip.show()
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def Fire(Repeat):
	if SunState() is 'Day': return
	MQTT("Fire")
	if Debug is True:
		print 'Fire',
		TimerStart = time.time()
	color1=CRed
	color2=COrange
	color3=CBlack
	Length=1
	Wait=.001
	for i in range (0, Repeat, 1):
		for j in range (0, LED_Last, Length):
			for h in range(0, Length, 1):
				strip.setPixelColor(j+h, color1)
			colorT = color1
			color1 = color2
			color2 = color3
			color3 = colorT
		strip.show()
		time.sleep(.07)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)
	
def Fuse(color1):
	if SunState() is 'Day': return
	MQTT("Fuse")
	if Debug is True:
		TimerStart = time.time()
		print 'Fuse',
		print(ColorCk(color1)),
	for i in range (LED_Last, 0, -1):
		strip.setPixelColor(i, color1)
		strip.setPixelColor(i+1, CBlack)
		strip.show()
		time.sleep(.001)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def FuseRev(color1):
	if SunState() is 'Day': return
	MQTT("FuseRev")
	if Debug is True:
		TimerStart = time.time()
		print 'FuseRev',
		print(ColorCk(color1)),
	for i in range (0, LED_Last, 1):
		strip.setPixelColor(i, color1)
		strip.setPixelColor(i-1, CBlack)
		strip.show()
		time.sleep(.001)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def FuseMulti(color1):
	if SunState() is 'Day': return
	MQTT("FuseMulti")
	if Debug is True:
		TimerStart = time.time()
		print 'FuseMulti',
		print(ColorCk(color1)),
	for i in range (LED_Last, 0, -1):
		for j in range (0, LED_Last, 30):
			a = i-j
			b = i+j
			c = i-j+1
			d = i-j-1
			e = i+j+1
			f = i-j-1
			if LED_Last >= a >= LED_First: strip.setPixelColor(a, color1)
			if LED_Last >= b >= LED_First: strip.setPixelColor(b, color1)
			if LED_Last >= c >= LED_First: strip.setPixelColor(c, CBlack)
			if LED_Last >= d >= LED_First: strip.setPixelColor(d, CBlack)
			if LED_Last >= e >= LED_First: strip.setPixelColor(e, CBlack)
			if LED_Last >= f >= LED_First: strip.setPixelColor(f, CBlack)
		strip.show()
		time.sleep(.001)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def FuseMultiRev(color1):
	if SunState() is 'Day': return
	MQTT("FuseMultiRev")
	if Debug is True:
		TimerStart = time.time()
		print 'FuseMultiRev',
		print(ColorCk(color1)),
	for i in range (0, LED_Last, 1):
		for j in range (LED_Last, 0, -30):
			a = i-j
			b = i+j
			c = i-j+1
			d = i-j-1
			e = i+j+1
			f = i+j-1
			if LED_Last >= a >= LED_First: strip.setPixelColor(a, color1)
			if LED_Last >= b >= LED_First: strip.setPixelColor(b, color1)
			if LED_Last >= c >= LED_First: strip.setPixelColor(c, CBlack)
			if LED_Last >= d >= LED_First: strip.setPixelColor(d, CBlack)
			if LED_Last >= e >= LED_First: strip.setPixelColor(e, CBlack)
			if LED_Last >= f >= LED_First: strip.setPixelColor(f, CBlack)
		strip.show()
		time.sleep(.001)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def FuseDance(color1):
	if SunState() is 'Day': return
	MQTT("FuseDance")
	if Debug is True:
		TimerStart = time.time()
		print 'FuseDance',
		print(ColorCk(color1)),
	for k in range (1, 5):
		for i in range (0, 30, 1):
			for j in range (LED_Last, 0, -30):
				a = i+j
				b = LED_Last-i-j
				c = a+1
				d = a-1
				e = i-j+1
				f = i-j-1
				g = b+1
				h = b-1
				if LED_Last >= a >= LED_First: strip.setPixelColor(a, color1)
				if LED_Last >= b >= LED_First: strip.setPixelColor(b, color1)
				if LED_Last >= c >= LED_First: strip.setPixelColor(c, CBlack)
				if LED_Last >= d >= LED_First: strip.setPixelColor(d, CBlack)
				if LED_Last >= e >= LED_First: strip.setPixelColor(e, CBlack)
				if LED_Last >= f >= LED_First: strip.setPixelColor(f, CBlack)
				if LED_Last >= g >= LED_First: strip.setPixelColor(g, CBlack)
				if LED_Last >= h >= LED_First: strip.setPixelColor(h, CBlack)
				if DebugLoop is True:
					PrintTemp = "k=" + str(k) + "\t i=" + str(i) + "\t j=" + str(j) + "\t a=" + str(a) + "\t b=" + str(b) + "\t c=" + str(c) + "\t d=" + str(d) + "\t e=" + str(e) + "\t f=" + str(f) + "\t g=" + str(g) + "\t h=" + str(h)
					print (PrintTemp)
					time.sleep(0)
			strip.show()
			time.sleep(.001)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def FuseDanceColor():
	if SunState() is 'Day': return
	MQTT("FuseDanceColor")
	if Debug is True:
		TimerStart = time.time()
		print 'FuseDanceColor,'
	color1 = CRed
	color2 = CGreen
	color3 = CBlue
	colorT = color1
	for z in range (1, 10):
		for k in range (1, 7):
			for i in range (0, 30, 1):
				for j in range (LED_Last, 0, -30):
					a = i+j
					b = LED_Last-i-j
					c = a+1
					d = a-1
					e = i-j+1
					f = i-j-1
					g = b+1
					h = b-1
					if LED_Last >= a >= LED_First: strip.setPixelColor(a, colorT)
					if LED_Last >= b >= LED_First: strip.setPixelColor(b, colorT)
					if LED_Last >= c >= LED_First: strip.setPixelColor(c, CBlack)
					if LED_Last >= d >= LED_First: strip.setPixelColor(d, CBlack)
					if LED_Last >= e >= LED_First: strip.setPixelColor(e, CBlack)
					if LED_Last >= f >= LED_First: strip.setPixelColor(f, CBlack)
					if LED_Last >= g >= LED_First: strip.setPixelColor(g, CBlack)
					if LED_Last >= h >= LED_First: strip.setPixelColor(h, CBlack)
					if i == 26:
						color1 = color2
						color2 = color3
						color3 = colorT
						colorT = color1
					if DebugLoop is True:
						PrintTemp = "k=" + str(k) + "\t i=" + str(i) + "\t j=" + str(j) + "\t a=" + str(a) + "\t b=" + str(b) + "\t c=" + str(c) + "\t d=" + str(d) + "\t e=" + str(e) + "\t f=" + str(f) + "\t g=" + str(g) + "\t h=" + str(h)
						print (PrintTemp)
						time.sleep(.1)
				strip.show()
				time.sleep(.02)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def FuseDanceColorMulti():
	if SunState() is 'Day': return
	MQTT("FuseDanceColorMulti")
	if Debug is True:
		TimerStart = time.time()
		print 'FuseDanceColorMulti,'
	color1 = CRed
	color2 = CRed
	color3 = COrange
	color4 = COrange
	color5 = CBlue
	color6 = CBlue
	color7 = CGreen
	color8 = CGreen
	color9 = CCyan
	color10 = CCyan
	color11 = CYellow
	color12 = CYellow
	color13 = CPurple
	color14 = CPurple
	colorT = color1
	for z in range (1, 11):
		for k in range (1, 7):
			for i in range (0, 30, 1):
				for j in range (LED_Last, 0, -30):
					a = i+j
					b = LED_Last-i-j
					c = a+1
					d = a-1
					e = i-j+1
					f = i-j-1
					g = b+1
					h = b-1
					if LED_Last >= a >= LED_First: strip.setPixelColor(a, colorT)
					if LED_Last >= b >= LED_First: strip.setPixelColor(b, colorT)
					if LED_Last >= c >= LED_First: strip.setPixelColor(c, CBlack)
					if LED_Last >= d >= LED_First: strip.setPixelColor(d, CBlack)
					if LED_Last >= e >= LED_First: strip.setPixelColor(e, CBlack)
					if LED_Last >= f >= LED_First: strip.setPixelColor(f, CBlack)
					if LED_Last >= g >= LED_First: strip.setPixelColor(g, CBlack)
					if LED_Last >= h >= LED_First: strip.setPixelColor(h, CBlack)
					if i == 26:
						color1 = color2
						color2 = color3
						color3 = color4
						color4 = color5
						color5 = color6
						color6 = color7
						color7 = color8
						color8 = color9
						color9 = color10
						color10 = color11
						color11 = color12
						color12 = color13
						color13 = color14
						color14 = colorT
						colorT = color1
					if DebugLoop is True:
						PrintTemp = "k=" + str(k) + "\t i=" + str(i) + "\t j=" + str(j) + "\t a=" + str(a) + "\t b=" + str(b) + "\t c=" + str(c) + "\t d=" + str(d) + "\t e=" + str(e) + "\t f=" + str(f) + "\t g=" + str(g) + "\t h=" + str(h)
						print (PrintTemp)
						time.sleep(.1)
				strip.show()
				time.sleep(.02)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def rainbow(wait_ms=20, iterations=1):
	''' Draw rainbow that fades across all pixels at once '''
	if SunState() is 'Day': return
	MQTT("rainbow")
	if Debug is True:
		TimerStart = time.time()
		print 'rainbow',
	for j in range(256*iterations):
		for i in range(LED_Last):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def rainbowCycle(wait_ms=20, iterations=5):
	''' Draw rainbow that uniformly distributes itself across all pixels '''
	if SunState() is 'Day': return
	MQTT("rainbowCycle")
	if Debug is True:
		TimerStart = time.time()
		print 'rainbowCycle',
	for j in range(256*iterations):
		for i in range(LED_Last):
			strip.setPixelColor(i, wheel(((i * 256 / LED_Last) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def theaterChase(color, wait_ms=50, iterations=10):
	''' Movie theater light style chaser animation '''
	if SunState() is 'Day': return
	MQTT("theaterChase")
	if Debug is True:
		TimerStart = time.time()
		print 'theaterChase',
		print(ColorCk(color)),
	for j in range(iterations):
		for q in range(3):
			for i in range(0, LED_COUNT, 3):
				strip.setPixelColor(i+q, color)
			strip.show()
			time.sleep(wait_ms/100.0)
			for i in range(0, LED_COUNT, 3):
				strip.setPixelColor(i+q, 0)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def theaterChaseRainbow(wait_ms=50):
	''' Rainbow movie theater light style chaser animation '''
	if SunState() is 'Day': return
	MQTT("theaterChaseRainbow")
	if Debug is True:
		TimerStart = time.time()
		print 'theaterChaseRainbow',
	for j in range(256):
		for q in range(3):
			for i in range(0, LED_Last, 3):
				strip.setPixelColor(i+q, wheel((i+j) % 255))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, LED_Last, 3):
				strip.setPixelColor(i+q, 0)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def TriWipe(color1, color2, color3, loops):
	''' Wipe three colors alternating '''
	if SunState() is 'Day': return
	MQTT("TriWipe")
	if Debug is True:
		TimerStart = time.time()
		print 'TriWipe',
		print(ColorCk(color1)),
		print(ColorCk(color2)),
		print(ColorCk(color3)),
		print(loops),
	for j in range(0,loops,1):
		for h in range(0,LED_Last,3):
			strip.setPixelColor(h,color3)
			strip.setPixelColor(h+1,color2)
			strip.setPixelColor(h+2,color1)
		strip.show()
		time.sleep(1)
		color4 = color3
		color3 = color2
		color2 = color1
		color1 = color4
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def TriWipe2(color1, color3, color5, loops):
	''' Wipe three colors alternating with black seperating LEDs '''
	if SunState() is 'Day': return
	MQTT("TriWipe2")
	if Debug is True:
		TimerStart = time.time()
		print 'TriWipe2',
		print(ColorCk(color1)),
		print(ColorCk(color3)),
		print(ColorCk(color5)),
		print 'loops =',
		print(loops),
	color2 = CBlack
	color4 = CBlack
	color6 = CBlack
	for j in range(0,loops,1):
		for h in range(0,LED_Last,6):
			strip.setPixelColor(h,color6)
			strip.setPixelColor(h+1,color5)
			strip.setPixelColor(h+2,color4)
			strip.setPixelColor(h+3,color3)
			strip.setPixelColor(h+4,color2)
			strip.setPixelColor(h+5,color1)
		strip.show()
		time.sleep(1)
		colorT = color6
		color6 = color5
		color5 = color4
		color4 = color3
		color3 = color2
		color2 = color1
		color1 = colorT
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def TriForce(color1, color2, color3, Length, Wait, Repeat):
	''' Wipe three colors alternating at a specified length '''
	''' Length is how many LEDs of a color in a row '''
	''' Wait is the delay time to update the next loop '''
	''' Repeat is how many times to loop '''
	if SunState() is 'Day': return
	MQTT("TriForce")
	if Debug is True:
		TimerStart = time.time()
		print 'TriForce',
		print(ColorCk(color1)),
		print(ColorCk(color2)),
		print(ColorCk(color3)),
		print 'Length =',
		print(Length),
		print 'Wait =',
		print(Wait),
		print 'Repeat =',
		print(Repeat),
	for i in range (0, Repeat, 1):
		for j in range (0, LED_Last, Length):
			for h in range(0, Length, 1):
				strip.setPixelColor(j+h, color1)
			colorT = color1
			color1 = color2
			color2 = color3
			color3 = colorT
			strip.show()
			time.sleep(Wait)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def TriSwipe(color1, color2, color3, Length, Wait, Repeat):
	''' Wipe three colors alternating at a specified length '''
	''' Length is how many LEDs of a color in a row '''
	''' Wait is the delay time to update the next loop '''
	''' Repeat is how many times to loop '''
	if SunState() is 'Day': return
	MQTT("TriSwipe")
	if Debug is True:
		TimerStart = time.time()
		print 'TriSwipe',
		print(ColorCk(color1)),
		print(ColorCk(color2)),
		print(ColorCk(color3)),
		print 'Length =',
		print(Length),
		print 'Wait =',
		print(Wait),
		print 'Repeat =',
		print(Repeat),
	for i in range (0, Repeat, 1):
		for j in range (0, LED_Last, Length*3):
			for h in range(0, Length, 1):
				strip.setPixelColor(j+h, color1)
			colorT = color1
			color1 = color2
			color2 = color3
			color3 = colorT
			strip.show()
			time.sleep(Wait)
	if Debug is True:
		TimerStop = time.time()
		Timer = TimerStop - TimerStart
		print (PYellow),
		print (Timer),
		print (POff)

def wheel(pos):
	''' Generate rainbow colors across 0-255 positions '''
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

'''
def cw(LTR):
	# Morse Code translation
	if Debug is True:
		print 'Morse Code',
		print(LTR)
	cwL = 50 # Length of pulse in mSec
	DIT = cwL # Length of pulse in mSec
	DAH = 3*cwL # Length of pulse in mSec
	BitGap = cwL # Length of space between characters
	LtrGap = 3*cwL
	WrdGap = 7*cwL
	#if LTR is 'A' or 'a'
'''

def AllTest():
	''' Display examples of LED effects '''
	if Debug is True: print 'AllTest'
	TriForce(CRed,CBlue,CGreen,10,1,3)
	TriForce(CRed,CBlue,CGreen,1,.05,5)
	TriForce(CRed,CBlue,CGreen,3,.05,15)
	Fire(75)
	TriWipe(CRed,CWhite,CBlue,25)
	TriWipe2(CRed,CWhite,CBlue,25)
	TriWipe(CRed,CGreen,CBlue,25)
	TriWipe2(CRed,CGreen,CBlue,25)
	TriWipe(COrange,CPink,CYellow,25)
	TriWipe2(COrange,CPink,CYellow,25)
	TriSwipe(CRed,CWhite,CBlue,10,1,10)
	# Fuse colors along string
	Fuse(CWhite)
	FuseRev(CRed)
	Fuse(CBlue)
	FuseRev(CGreen)
	Fuse(CCyan)
	FuseRev(CPurple)
	Fuse(CPink)
	FuseRev(CRedLt)
	Fuse(COrange)
	FuseRev(CYellow)
	Fuse(CCyan)
	# Color wipe animations.
	colorWipe(CRed)
	colorWipeRev(COrange)
	colorWipe(CBlue)
	colorWipeRev(CPink)
	colorWipe(CPink2)
	colorWipeRev(CGreen)
	colorWipe(CYellow)
	DualWipe(CRed, CGreen)
	time.sleep(3)
	DualWipe(CGreen, CBlue)
	time.sleep(3)
	DualWipe(CBlue, CRed)
	time.sleep(3)
	DualWipe(CPink, CPink2)
	time.sleep(3)
	# Theater chase animations.
	theaterChase(CWhite)
	theaterChase(CRed)
	theaterChase(CBlue)
	# Rainbow animations.
	rainbow()
	time.sleep(3)
	rainbowCycle()
	theaterChaseRainbow()
	Vday()
	Thanksgiving()
	Christmas()
	Easter()
	BDay()
	Patriotic()
	UW()
	StPDay()
	Navy()

def MQTT(MQ_Func):
	# Send to the MQTT Broker
	try:
		if MQTT_enable is True:
			#now = datetime.datetime.now()
			#MQTT_time = str(now)
			now = datetime.datetime.now()
			ETime = str(now.strftime("at %H:%M:%S on %m-%d-%Y"))
			mqttc = mqtt.Client("python_pub")
			mqttc.connect(Broker_IP, Broker_Port)
			mqttc.publish("lights/Function", MQ_Func) # Function Name
			mqttc.publish("lights/Holiday", mq_holiday) # Holiday Name
			mqttc.publish("lights/Easter", ED) # Easter Date
			mqttc.publish("lights/Time", ETime) # Time of MQTT Update
			mqttc.publish("lights/Debug", Debug)
			if Debug is True:
				### Maybe makes this a one time publish per execution along with all the Debug info at the begining
				print "MQTT updated"
				print (ETime)
				print (MQ_Func)
				print (mq_holiday)
				print (ED)
				print (Debug)
		if MQTT_enable is False:
			if Debug is True:
				print "MQTT is not enabled"
	except:
		# Prevent crashing if Broker is disconnected
		if Debug is True:
			print "MQTT Failed"
			
#########

# Main program:
try:
	if __name__ == '__main__':
		# Create NeoPixel object with appropriate configuration.
		strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
		# Intialize the library (must be called once before other functions).
		strip.begin()
		strip.show()
		blackout()
		# Set LastOn and LastOff in event of exit before reaching either state
		if Debug is True: print 'Debug is ON'
		if Debug is False: print 'Debug is OFF'
		sys.flush()
		if Debug is True:
			print ('Press \033[1m Ctrl-C \033[0m to quit.')
			print (PBlue),
			print ('It is currently'),
			print (PYellow),
			print SunState(),
			print (PBlue),
			print ('on'),
			print (PPurple),
			print Holiday(),
			print (POff),
			sys.flush()
		while True:
			#AllTest() # Functions setup for individual testing
			mq_holiday = "None"
			while Holiday() != 'None':
				''' Only checks if a Holiday '''
				while SunState() is 'Night':
					''' Only checks after Night '''
					while Holiday() is 'UW' and SunState() is 'Night':
						mq_holiday = "UW"
						UW()
					while Holiday() is 'Birthday' and SunState() is 'Night':
						mq_holiday = "Birthday"
						BDay()
					while Holiday() is 'Valentine' and SunState() is 'Night':
						mq_holiday = "Valentine"
						Vday()
					while Holiday() is 'Patriotic' and SunState() is 'Night':
						mq_holiday = "Patriotic"
						Patriotic()
					while Holiday() is 'Christmas' and SunState() is 'Night':
						mq_holiday = "Christmas"
						Christmas()
					while Holiday() is 'StPatrick' and SunState() is 'Night':
						mq_holiday = "StPatrick"
						StPDay()
					while Holiday() is 'Easter' and SunState() is 'Night':
						mq_holiday = "Easter"
						Easter()
					while Holiday() is 'ParentDay' and SunState() is 'Night':
						mq_holiday = "ParentDay"
						Parent()
					while Holiday() is 'Autism' and SunState() is 'Night':
						mq_holiday = "Autism"
						Autism()
					while Holiday() is 'Premmie' and SunState() is 'Night':
						mq_holiday = "Premie"
						Premmie()
					while Holiday() is 'HydroC' and SunState() is 'Night':
						mq_holiday = "HydroC"
						HydroC()
					while Holiday() is 'CPDay' and SunState() is 'Night':
						mq_holiday = "CPDay"
						CPDay()
					while Holiday() is 'DisabilityDay' and SunState() is 'Night':
						mq_holiday = "DisabilityDay"
						DisabilityDay()
					while Holiday() is 'Family' and SunState() is 'Night':
						mq_holiday = "Family"
						Familyday()
					# **** Disabled for Now ****
					#while Holiday() is 'Navy' and SunState() is 'Night':
					#	Navy()
					#while Holiday() is 'Thanksgiving' and SunState() is 'Night':
					#	Thanksgiving()
					blackout() # Ensures lights turn off immediatly following Holiday at Midnight
					time.sleep(60*5) # Pause between Days
				time.sleep(60*5) # Pause between Day and Night
			MQTT("None")
			time.sleep(60*5) # Prevents repeatedly checking Holiday() rotine when not a holiday

except KeyboardInterrupt:
	sys.flush()
	print (PRed),
	print 'Interrupted by User at keyboard'
	print (POff),
	print (PYellow),
	print SunState(),
	print (PBlue),
	print datetime.datetime.now()
	print (POff),
	sys.flush()
	print 'Turning off lights'
	sys.flush()
	blackout()
	print ' quit '
	quit()

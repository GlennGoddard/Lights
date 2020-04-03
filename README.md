# Lights
Christmas Lights ++

## Description

Control Script for individually addressable LEDs.  
Lights will only come on after sunset and stay on until sunrise for the respective holiday.  
Several holidays are setup.  
I am especially proud of my Easter calculation.  This took me a little bit of time to figure out.  
Christmas routine starts the day after Thanksgiving until All King's Day (January 6).  
For those with children, the ParentDay routine which runs on Mother's Day and Father's Day.  Some adjustment will be needed to adjust it to your situation.  The birthstone will be lit for the years of age of each child. (Future update is to add a space between to handle more than one birth in a month; clarification, it can handle it, you just can not tell when one ends and the other begins)  

Sunrise and Sunset are based on actual location, not a general location; LAT and Long are in decimal not mins and secs.  (Need to add instructions to obtain decimal position from Google Maps)  

As of now, MQTT if using Debug will always show failed on the first attempt.  This is because on the first run of MQTT routine not all variables and other support functions have run at startup.  This is expected behavior.  The first few MQTT items will publish, this just demonstrates that the error trap works.  MQTT is not set to save any data on broker, this is why all data is sent everytime; I like it this way, so it is unlikely to change.

I have a lot more comments to add to the readme file; but I am posting this finally after a few years so everyone has access to it.  I have given different versions to people over the years but this is just easier.  Enjoy.  

### Holidays

Birthday - Add and adjust as needed  
Valentine's Day is 2/14  
Saint Patricks Day 3/17  
Easter is between 3/22 and 4/25. 1st Sunday after the full moon that occurs on or next after the vernal equinox (March 21)  
National Cerebral Palsy Awareness Day is 3/25  
World Autism Awareness Day is 4/2  
Mothers Day is 2nd Sunday in May (change birthyears as needed if Birthday is after Mother's Day then subtract one from the year)  
Disability Awareness Day is the 3rd Thursday of May  
Fathers Day is 3rd Sunday in June (change birthyears as needed if Birthday is after Fathers's Day then subtract one from the year)  
Independance Day July 4, 1776  
Family Day is the 1st Sunday in August (change birthyears as needed if Birthday is after Familiy Day then subtract one from the year)  
National Hydrocephalus Awareness Day is 9/21  
World Cerebral Palsy Awareness Day is 1st Wensday in October  
World Hydrocephalus Awareness Day is 10/25  
Veterans Day is 11/11  
World Prematurity Awareness Day is 11/17  
Christmas lights are from day after Thanksgiving until January 6  

### MQTT
List of MQTT Topics  
  
Debug - True or False  
DebugUTC - True or False
ForceNight - True or False  
Easter - Date of Easter this year   
Function - Current Function running  
Holiday - Holiday Name today  
Brightness - LED 0-255  
Count - Number of total LEDs  
DMA - DMA Setting  
Frequency - PWM Frequency in Hz  
Invert - Control inverted True or False  
Pin - GPIO Pin for PWM  
Latitude - Location for Sun Position  
Longitude - Location for Sun Position  
SunState - Day or Night  
Time - Time of last MQTT post  

## Change Log

3/22/2020  
Initial GitHub upload after six years of personal use.  

4/2/2020  1300  
Fixed an MQTT Variable that occasionally caused a MQTT failure.  
Updated MQTT to include more Topics, also established sub Topics.  

4/2/2020 2100
Updated Debug tags in MQTT routine  
Added Topic Count in MQTT  

## Things to Add / Contemplate

Change MQTT to add the last time each function was run - Maybe.  
Reduce MQTT publish (need to rework, might delay some info such as function calls to not be real time).  
Modify ParentDay / FamilyDay routine to add space between each birthday  
Fully implement DebugDate  
Enable MQTT for SunAngle (maybe a seperate function, had issues with a global variable inside the SunState routine)  
Add MQTT for Sunrise and Sunset times  
Add MQTT for Thanksgiving which in turn gives the next date for Christmas light routine  
Add MQTT for all holiday dates??? (or maybe a countdown to each)  
Add routine calls variables??? (not a constant amount, is this worth the effort???)

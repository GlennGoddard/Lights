# Lights
Christmas Lights ++

Control Script for individually addressable LEDs.
Lights will only come on after sunset and stay on until sunrise for the respective holiday.
Several holidays are setup.
I am especially proud of my Easter calculation.  This took me a little bit of time to figure out.
Christmas routine starts the day after Thanksgiving until All King's Day (January 6)
For those with children, the ParentDay routine which runs on Mother's Day and Father's Day.  Some adjustment will be needed to adjust it to your situation.  The birthstone will be lit for the years of age of each child. (Future update is to add a space between to handle more than one birth in a month.)

Sunrise and Sunset are based on actual location, not a general location; LAT and Long are in decimal not mins and secs.  (Need to add instructions to obtain decimal position from Google Maps)

I have a lot more comments to add to the readme file; but I am posting this finally after a few years so everyone has access to it.  I have given different versions to people over the years but this is just easier.  Enjoy.

# Change Log

4/2/2010  1300
Fixed an MQTT Variable that occasionally caused a MQTT failure
Updated MQTT to include more Topics, also established sub Topics

# Things to Add / Contemplate

Change MQTT to add the last time each function was run - Maybe
Reduce MQTT publish (need to rework, might delay some info such as function calls to not be real time)

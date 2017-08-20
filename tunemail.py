################################################################
#   tunemail: a useless and dangerous social IoT alarm clock   # 
################################################################

# !/usr/bin/python

import RPi.GPIO as GPIO
import pygame
import gmail
from subprocess import *
from Adafruit_CharLCD import Adafruit_CharLCD
from time import sleep, strftime
from datetime import datetime

# GPIO setup
GPIO.setmode(GPIO.BCM)
# pin 4 has internal pull-up and pull-down resistors; enable pull-up
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# pins 2 = SDA and pin 3 = SCL already have pull-up resistors by default
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)

# LCD setup
lcd = Adafruit_CharLCD.Adafruit_CharLCD()
lcd.begin(16, 1)
lcd.leftToRight()

# audio setup
pygame.mixer.init()

# global variables and their default values
alarm_time = 0         
alarm_on = False
setting_now = False
next_song = "yourfavoritesonghere"  #this song plays if the alarm's queue is empty
gmail_name = "yourusernamehere"
gmail_pw = "yourpasswordhere"


# display long, sentence-like messages on the LCD
# for now, input should not contain newlines
def displayText(text):

	lcd.clear()
	lcd.begin(16, 2)
	lcd.leftToRight()

	# i counts the index of a char on a given line 
    # k counts the line parity.
	i, k = 0, 0
	for char in text:
        chars_left_in_line = (16 - i) % 16
        # if there are enough chars left in the line, don't worry about breaks.
        if chars_left_in_line >= len(text):
                lcd.message(char)
                i = i + 1
        # otherwise, break at the last possible space for odd lines
        # break by clearing the screen for even lines
		else:
            rest_of_line = [text[n] for n in range(1, 1 + chars_left_in_line)]
            if char == ' ' and not ' ' in rest_of_line:
                if k == 0:
                    lcd.message('\n')
                    i, k = 0, 1
                else:
                    lcd.clear()
                    i, k = 0, 0
            elif chars_left_in_line == 1:
				lcd.message(char)
				if k == 0:
					lcd.message('\n')
					i, k = 0, 1
				else:
					lcd.clear()
					i, k = 0, 0
            else:
                lcd.message(char)
                i = i + 1
        	text = text[1:len(text)]
        	sleep(.1)
	lcd.clear()


# check for new email, then download and process all .mp3 attachments
def checkMail():
    global gmail_name
    global gmail_pw

	g = gmail.login(gmail_name, gmail_pw)
	newmail = g.inbox().mail(unread=True)

	for email in newmail:
        email.fetch()
        for attachment in email.attachments:
            if attachment.name[(len(attachment.name) - 4):len(attachment.name)] == '.mp3':
                attachment.save("/home/pi/music/" + attachment.name)
                    with open("/home/pi/music/unplayedsongs.txt", "a") as unplayed:
                        unplayed.write(attachment.name + "\n")
        email.read()	
	g.logout()


# get the next song from the unplayed list, then move that song to the played list

def getNextSong():
	global next_song
        with open("/home/pi/music/unplayedsongs.txt", "r") as unplayed:
            lines = unplayed.readlines()
		#if there are no unplayed songs, play the default song.
		if lines:
            next_song = lines[0]

        with open("/home/pi/music/unplayedsongs.txt", "w") as unplayed:
            unplayed.writelines(lines[1:])

        with open("/home/pi/music/playedsongs.txt", "a") as played:
            played.seek(0)
		if lines:
			played.writelines(next_song)
        
	next_song = next_song[:-1]
	return next_song 



# convert from raw minutes to 24-hour time

def hours(time):
	return ((time % 1440) - (time % 60))/60

def mins(time):
	return (time % 60)

# alarm setting functions

def setAlarm(channel):
	sleep(.5)
	global alarm_time
	global alarm_on
	global setting_now
	if not GPIO.input(channel):
		setting_now = True
		lcd.clear()
		lcd.message("Setting alarm:\n")
		lcd.message(str(hours(alarm_time)).zfill(2)+":"+str(mins(alarm_time)).zfill(2))
        # momentary switch on pin 2 moves alarm time forward
		GPIO.add_event_detect(2, GPIO.FALLING, callback=increment, bouncetime=300)
        # momentary switch on pin 3 moves alarm time backwards
		GPIO.add_event_detect(3, GPIO.FALLING, callback=decrement, bouncetime=300)
	else:
		lcd.clear()
		lcd.message("Alarm is now set\n")
		lcd.message("for "+str(hours(alarm_time)).zfill(2)+":"+str(mins(alarm_time)).zfill(2))
		GPIO.remove_event_detect(2)
		GPIO.remove_event_detect(3)
		sleep(5)
		lcd.clear()
		setting_now = False
		alarm_on = True
	

def increment(channel):
	global alarm_time
	while not GPIO.input(channel):
		alarm_time = alarm_time + 1
		lcd.clear()
		lcd.message("Setting alarm:\n")	
		lcd.message(str(hours(alarm_time)).zfill(2)+":"+str(mins(alarm_time)).zfill(2))  
		sleep(.2)

def decrement(channel):
	global alarm_time
	while not GPIO.input(channel):
		alarm_time = alarm_time - 1
		lcd.clear()
		lcd.message("Setting alarm:\n")
		lcd.message(str(hours(alarm_time)).zfill(2)+":"+str(mins(alarm_time)).zfill(2)) 
		sleep(.2)

# assign the setAlarm function to the latching switch on pin 4

GPIO.add_event_detect(4, GPIO.FALLING, callback=setAlarm, bouncetime= 1000)


# main loop: displays current time and alarm time by default
# with interrupts for alarm setting and alarm sounding

while True:
	global alarm_time
	global alarm_on
	global setting_now
	global next_song
	while setting_now == False:
		lcd.clear()
		lcd.message(datetime.now().strftime('%b %d %H:%M:%S\n'))
		if alarm_on == True:
			lcd.message('Alarm: '+str(hours(alarm_time)).zfill(2)+":"+str(mins(alarm_time)).zfill(2))
			now = datetime.now()
			if now.hour == hours(alarm_time) and now.minute == mins(alarm_time):
				checkMail()
				getNextSong()
				pygame.mixer.music.load("/home/pi/music/"+next_song)
				pygame.mixer.music.play()
				lcd.clear()
				while pygame.mixer.music.get_busy() == True:
					displayText(next_song)
				lcd.clear()
				alarm_on = False

		else:
			lcd.message('Alarm: off')
		sleep(1)

GPIO.cleanup()



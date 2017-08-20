##############################################################
#  tunemail: a useless and dangerous social IoT alarm clock  #
##############################################################

Just in case your life is not complete without an alarm clock
which checks your email and indiscriminately downloads attachments. If you build this, and if it's 2008
and your friends send you emails with .mp3 attachments, your
alarm clock will definitely know about it and play those mp3s
to wake you up in the morning. Or at whatever time of day you
want to wake up. Disclaimer: this is a bad idea. 

Materials: 
Revision B Raspberry Pi
Wifi adaptor or ethernet connection for RPi
Adafruit 16x2 RGB LCD display + potentiometer
1 latching button or switch
2 momentary buttons or switches
Throwaway gmail account

Setup: 
1. On the RPi, make a directory "home/pi/music" and put in it: (a) your favorite song (to be used as a default alarm), (b) an empty (!) file "unplayedsongs.txt", and (c) an empty (!) file "playedsongs.txt." 
2. Install the dependencies of tunemail.py on the RPi.
3. Edit "Adafruit_CharLCD" to replace "21" with "27" in the pin list (this is rev B-specific).
4. Wire up the Adafruit 16x2 RGB LCD and potentiometer as in their tutorial. 
5. Connect GPIO pin 4 to one terminal of a latching button and connect the other terminal of the button to ground. 
6. Connect the SDA pin to one terminal of a momentary button and connect the other terminal to ground. Connect the SCL pin to one terminal of a second momentary button and connect the other terminal to ground. 
7. Edit the default values of the global variables in tunemail.py with your gmail info and default song name.
8. Connect your RPi to the internet, make sure the timezone
is set properly, and run tunemail.py.

Use:
1. Give your friends the gmail address and ask them to send you songs as .mp3 attachments.
2. Don't worry, if your friends think this is a bad idea, 
don't listen to you, or don't know what an mp3 is, your
default song will still wake you up.
3. To set the alarm, press the latching button once, then use
the two momentary buttons to scroll to your wake-up time. Then
press the latching button again. 
4. Sweet dreams!

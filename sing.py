# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 03:22:07 2025

@author: CW
"""

#! /usr/bin/python2

from naoqi import ALProxy

# Set Pepper's IP and Port
PEPPER_IP = "192.168.0.109"  # Change this to match your Pepper's IP
PORT = 9559

# Create NAOqi Proxies
tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)
animated_speech = ALProxy("ALAnimatedSpeech", PEPPER_IP, PORT)
tablet = ALProxy("ALTabletService", PEPPER_IP, PORT)

def pepper_ipadPrint(text):
    """Display text on Pepper's tablet."""
    tablet.showImage("http://198.18.0.1/apps/boot-config/startup.png")  # Default image
    tablet.executeJS("document.body.innerHTML = '<h1 style=\"font-size:50px; text-align:center;\">{}</h1>';".format(text))
    print("Displaying on tablet:", text)

def pepper_sing():
    """Make Pepper sing 'Rolling in the Deep' using Text-to-Speech."""
    print("Singing")
    pepper_ipadPrint("Singing Rolling in the Deep")  # Display on tablet

    lyrics = """
    \\rspd=70\\ There's a fire starting in my heart,
    \\pau=500\\ Reaching a fever pitch, and it's bringing me out the dark...
    \\rspd=80\\ The scars of your love remind me of us,
    \\pau=500\\ They keep me thinking that we almost had it all...
    """

    animated_speech.say(lyrics)
    tts.say("I hope you liked my song!")

if __name__ == "__main__":
    pepper_sing()

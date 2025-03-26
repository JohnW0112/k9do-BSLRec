# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 07:56:07 2025

@author: CW
"""

# -*- coding: utf-8 -*-
"""
Pepper detects music, flashes LED, shows tablet message, and sings a song
"""

#! /usr/bin/python2
from naoqi import ALProxy
import time

PEPPER_IP = "192.168.0.109"  # Replace with your Pepper's IP
PORT = 9559

# === Connect to NAOqi services ===
audio_device = ALProxy("ALAudioDevice", PEPPER_IP, PORT)
tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)
motion = ALProxy("ALMotion", PEPPER_IP, PORT)
leds = ALProxy("ALLeds", PEPPER_IP, PORT)
tablet = ALProxy("ALTabletService", PEPPER_IP, PORT)
animated_speech = ALProxy("ALAnimatedSpeech", PEPPER_IP, PORT)

motion.setStiffnesses("Body", 1.0)

# === Tablet display ===
def show_text_on_tablet(text):
    html = "<h1 style='font-size:40px; text-align:center; color:#007BFF;'>{}</h1>".format(text)
    tablet.showImage("http://198.18.0.1/apps/boot-config/startup.png")
    tablet.executeJS("document.body.innerHTML = '{}'".format(html))

# === LED flash animation ===
def flash_eyes(times=3, color="white"):
    group = "FaceLeds"
    for i in range(times):
        leds.fadeRGB(group, 0xFFFFFF, 0.2)  # White ON
        time.sleep(0.2)
        leds.fadeRGB(group, 0x000000, 0.2)  # OFF
        time.sleep(0.2)

# === Singing function ===
def sing_twinkle():
    show_text_on_tablet("🎵 Singing Twinkle Twinkle 🎶")
    tts.say("Let me sing a few lines for you.")
    lyrics = """
    \\rspd=70\\ Twinkle, twinkle, little star,
    \\pau=400\\ How I wonder what you are,
    \\pau=400\\ Up above the world so high,
    \\pau=400\\ Like a diamond in the sky.
    """
    animated_speech.say(lyrics)

# === Main: listen and respond ===
def listen_and_react(threshold=3000):
    print("🎧 Listening for music or loud sound...")
    show_text_on_tablet("Play some music! 🎶")

    for i in range(30):  # Approx. 15 seconds
        level = audio_device.getMicEnergy()
        print("Mic energy:", level)

        if level > threshold:
            print("🎵 Detected sound! Reacting...")
            flash_eyes()
            show_text_on_tablet("I hear music!")
            sing_twinkle()
            break

        time.sleep(0.5)

if __name__ == "__main__":
    listen_and_react()

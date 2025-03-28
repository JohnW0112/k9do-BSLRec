# -*- coding: utf-8 -*-


import speech_recognition as sr
from naoqi import ALProxy
import time

# ==== CONFIG ====
PEPPER_IP = "192.168.1.100"  # Replace with your Pepper's IP

# ==== Connect to Motion Proxy ====
motion = ALProxy("ALMotion", PEPPER_IP, 9559)
posture = ALProxy("ALRobotPosture", PEPPER_IP, 9559)

# ==== Move to Stand Init if not already ====
posture.goToPosture("StandInit", 0.5)

# ==== Define Raise Hands Action ====
def raise_hands():
    print("🙌 Raising hands...")
    # Joint names
    names = ["LShoulderPitch", "RShoulderPitch", "LElbowRoll", "RElbowRoll"]

    # Target angles in radians (hands up)
    angles = [-1.5, -1.5, -1.0, 1.0]
    fractionMaxSpeed = 0.3

    motion.setStiffnesses("Arms", 1.0)
    motion.angleInterpolation(names, angles, [1.0]*4, True)
    print("Hands raised.")

# ==== Listen for "surrender" ====
def listen_and_act():
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("Say 'surrender' to trigger the action...")

    with mic as source:
        r.adjust_for_ambient_noise(source)
        while True:
            print("Listening...")
            audio = r.listen(source)
            try:
                command = r.recognize_google(audio).lower()
                print("You said:", command)
                if "surrender" in command:
                    raise_hands()
                    break
            except sr.UnknownValueError:
                print(" Could not understand.")
            except sr.RequestError as e:
                print("Google Speech API error:", e)

# ==== Start ====
listen_and_act()

#! /usr/bin/python2

import socket
import struct
import numpy as np
from naoqi import ALProxy
import time
import argparse

# Pepper's IP and Port
PEPPER_IP = "192.168.0.109"  # Pepper IP
PORT = 9559

'''PARAMETERS'''
# Subscribe to the video feed
resolution = 3              # 1280x960
color_space = 13            # BGR color space
fps = 10                    # max fos = 30
'''
# Set up a server socket to receive messages
HOST = '127.0.0.1'  # Localhost
PORT_CONTROL = 5005  # For getting command
PORT_VIDEO = 5006 # For sending video feed
server_socket_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket_con.bind((HOST, PORT_CONTROL))
server_socket_con.listen(1)

print("Waiting for control connection from process.py...")
conn_con, addr_con = server_socket_con.accept()
print("Connected to:", addr_con)

server_socket_vid = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket_vid.bind((HOST, PORT_VIDEO))
server_socket_vid.listen(1)
print("Waiting for video feed connection from process.py...")
conn_vid, addr_vid = server_socket_vid.accept()
print("Connected to:", addr_vid)
'''
# Create proxy
'''
Everything you need from the NAOqi should be defined here. I just imported some basic proxies
'''
video_service = ALProxy("ALVideoRecorder", PEPPER_IP, PORT)
posture = ALProxy("ALRobotPosture", PEPPER_IP, PORT)
behavior = ALProxy("ALBehaviorManager", PEPPER_IP, PORT)
touch = ALProxy("ALTouch", PEPPER_IP, PORT)
tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)
photoCaptureProxy = ALProxy("ALPhotoCapture", PEPPER_IP, PORT)

def pepper_tts(word):
    #TODO: Text-2-speech
    print("TTS started...")

def pepper_ipadPrint(word):
    #TODO: Print words onto the ipad
    print("Printing words")

def pepper_call():
    #TODO: Call someone according to selected contact and display "Calling ${CONTACT}" output onto ipad.
    print("Select call contact")
    while (not data):
        data = conn_con.recv(1024).decode()
    
        if data:
            if (data == '1'):
                print("Calling contact 1")
                pepper_ipadPrint("Calling contact 1")
                pepper_tts("Calling contact 1")
                # Contact 1
            elif (data == '2'):
                print("Calling contact 2")
                pepper_ipadPrint("Calling contact 2")
                pepper_tts("Calling contact 2")
                # Contact 2
            elif (data == '3'):
                print("Calling contact 3")
                pepper_ipadPrint("Calling contact 3")
                pepper_tts("Calling contact 3")
                # Contact 3

def pepper_raiseArm():
    #TODO: Raise an arm
    print("Raising arm...")
    pepper_tts("Hi")
    

def pepper_sing():
    #TODO: Sing
    print("Singing...")

def pepper_summon():
    #TODO: Pepper respond to the call of its name, and move towards user
    print("Being summoned...")
    pepper_tts("On my way")

def pepper_checkTouch():
    print("Checking for touch...")
    touched_sensors = touch.getStatus()
    
    for sensor in touched_sensors:
        sensor_name = sensor[0]  # Name of the sensor
        is_touched = sensor[1]  # 1 if touched, 0 if not
        
        if is_touched:
            pepper_tts("Oh hi there, how can I help you")

            '''
            if "Head" in sensor_name:
                tts.say("head")
            elif "HandLeft" in sensor_name:
                tts.say("hand left")
            elif "HandRight" in sensor_name:
                tts.say("hand right")
            elif "Bumper" in sensor_name:
                tts.say("bumper")
            '''

if __name__=="__main__":
    try:
        # Get video feed and send to process.py
        tts.say("Hello")
        
        photoCaptureProxy.setResolution(2)
        photoCaptureProxy.setPictureFormat("jpg")
        photoCaptureProxy.takePictures(3, "C:/Users/Eldon/Desktop", "image")
        video_service.setFrameRate(10)
        video_service.setResolution(2) # Set resolution to VGA (640 x 480)
        # We'll save a 5 second video record in /home/nao/recordings/cameras/

        #while True:


            # This records a 320*240 MJPG video at 10 fps.
            # Note MJPG can't be recorded with a framerate lower than 3 fps.
        video_service.startRecording("C:/Users/Eldon/Desktop", "myvideo")

        time.sleep(5)

        # Video file is saved on the robot in the
        # /home/nao/recordings/cameras/ folder.
        videoInfo = video_service.stopRecording()
        print("Video was saved on the robot: ", videoInfo[1])
        print( "Total number of frames: ", videoInfo[0])
        '''
        data = conn_con.recv(1024).decode()
        if not data:
            continue


        if data == 'c':
            pepper_call()

        elif data == 'z':
            pepper_raiseArm()

        elif data == 'f':
            pepper_sing()'
        '''

    finally:

        ''' 
        conn_vid.close()
        conn_con.close()
        server_socket_vid.close()
        server_socket_con.close()'
        '''
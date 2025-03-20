#! /usr/bin/python2
# -*- coding: utf-8 -*-

import socket
import struct
import numpy as np
from naoqi import ALProxy
import qi
import time


# Pepper's IP and Port
# PEPPER_IP = "192.168.0.109"  # Pepper IP
PEPPER_IP = "localhost"
PORT = 57683

'''PARAMETERS'''
# Subscribe to the video feed
resolution = 3              # 1280x960
color_space = 13            # BGR color space
fps = 30                    # max fps = 30

# Set up a server socket to receive messages
HOST = '127.0.0.1'  # Localhost
PORT_CONTROL = 5684  # For getting command
PORT_VIDEO = 5007 # For sending video feed
server_socket_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket_con.bind((HOST, PORT_CONTROL))
server_socket_con.listen(1)

print("Waiting for control connection from process.py...")
conn_con, addr_con = server_socket_con.accept()
print("Connected to:", addr_con)

server_socket_vid = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket_vid.bind((HOST, PORT_VIDEO))
server_socket_vid.listen(1)
server_socket_vid.settimeout(10)  # Timeout to avoid blocking forever

print("Waiting for video feed connection from process.py...")
try:
    conn_vid, addr_vid = server_socket_vid.accept()
    print("Connected to:", addr_vid)
except socket.timeout:
    print("Warning: No video connection established. Continuing...")
    conn_vid = None


# Create proxy
# video_service = ALProxy("ALVideoDevice", PEPPER_IP, PORT)
try:
    video_service = ALProxy("ALVideoDevice", PEPPER_IP, PORT)
except RuntimeError:
    print("Error: Could not connect to Pepper on port {}. Is Choregraphe running?".format(PORT))
    exit(1)  # Exit the script if connection fails

posture = ALProxy("ALRobotPosture", PEPPER_IP, PORT)
behavior = ALProxy("ALBehaviorManager", PEPPER_IP, PORT)
touch = ALProxy("ALTouch", PEPPER_IP, PORT)

def pepper_tts(word):
    #TODO: Text-2-speech
    print("TTS started...")

def pepper_ipadPrint(word):
    #TODO: Print words onto the iPad
    print("Printing words")

def pepper_call():
    #TODO: Call someone according to selected contact and display "Calling ${CONTACT}" output onto iPad.
    print("Select call contact")
    data = None
    while not data:
        data = conn_con.recv(1024).decode()
    
        if data:
            if data == '1':
                print("Calling contact 1")
                pepper_ipadPrint("Calling contact 1")
                pepper_tts("Calling contact 1")
            elif data == '2':
                print("Calling contact 2")
                pepper_ipadPrint("Calling contact 2")
                pepper_tts("Calling contact 2")
            elif data == '3':
                print("Calling contact 3")
                pepper_ipadPrint("Calling contact 3")
                pepper_tts("Calling contact 3")

def pepper_raiseArm(action):
    """
    Controls Pepper's arms based on the specified action.
    Ensures compatibility with both Choregraphe and the real robot.
    :param action: str - one of ["left", "right", "both", "point", "wave"]
    """
    session = qi.Session()
    try:
        session.connect("tcp://127.0.0.1:9559")  # Connect to the real robot
        motion_service = session.service("ALMotion")
        print("Connected to real Pepper robot.")
    except RuntimeError:
        print("Running in Choregraphe mode (simulation).")
        motion_service = None  # No motion service in Choregraphe


    def set_angles(joint_names, angles, speed):
        if motion_service:
            motion_service.setAngles(joint_names, angles, speed)
        else:
            print("Simulating movement: {} -> {}".format(joint_names, angles))  # Fix for Python 2


    if action == "left":
        set_angles(["LShoulderPitch", "LElbowYaw", "LElbowRoll"], [-0.5, 0.0, -1.0], 0.2)

    elif action == "right":
        set_angles(["RShoulderPitch", "RElbowYaw", "RElbowRoll"], [-0.5, 0.0, 1.0], 0.2)

    elif action == "both":
        set_angles(["LShoulderPitch", "LElbowYaw", "LElbowRoll", "RShoulderPitch", "RElbowYaw", "RElbowRoll"],
                   [-0.5, 0.0, -1.0, -0.5, 0.0, 1.0], 0.2)

    elif action == "point":
        set_angles(["RShoulderPitch", "RElbowYaw", "RWristYaw"], [0.5, -1.5, 1.0], 0.2)

    elif action == "wave":
        for _ in range(3):
            set_angles(["RShoulderPitch", "RElbowYaw", "RElbowRoll"], [-0.5, 0.0, 1.0], 0.5)
            time.sleep(0.5)
            set_angles(["RShoulderPitch", "RElbowYaw", "RElbowRoll"], [-0.5, 0.0, 0.5], 0.5)
            time.sleep(0.5)

    else:
        print("Invalid action specified for pepper_raiseArm(). Choose from 'left', 'right', 'both', 'point', or 'wave'.")

def pepper_sing():
    #TODO: Sing
    print("Singing...")

def pepper_summon():
    #TODO: Pepper responds to being called and moves toward the user
    print("Being summoned...")
    pepper_tts("On my way")

def pepper_checkTouch():
    print("Checking for touch...")
    touched_sensors = touch.getStatus()
    
    for sensor in touched_sensors:
        sensor_name = sensor[0]
        is_touched = sensor[1]

        if is_touched:
            pepper_tts("Oh hi there, how can I help you")

if __name__ == "__main__":
    try:
        subscriber_id = video_service.subscribeCamera("pepper_stream", 0, resolution, color_space, fps)
        image_container = video_service.getImageRemote(subscriber_id)

        while True:
            if image_container:
                width, height = image_container[0], image_container[1]
                array = image_container[6]
                frame = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))

                conn_vid.sendall(struct.pack("L", len(frame.tobytes())) + frame.tobytes())

            data = conn_con.recv(1024).decode()
            if not data:
                break

            if data == 'c':
                pepper_call()

            elif data in ['left', 'right', 'both', 'point', 'wave']:
                pepper_raiseArm(data)

            elif data == 'f':
                pepper_sing()

    finally:
        video_service.unsubscribe(subscriber_id)
        conn_vid.close()
        conn_con.close()
        server_socket_vid.close()
        server_socket_con.close()

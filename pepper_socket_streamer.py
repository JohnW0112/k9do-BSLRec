#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

# counter part is live_gesture_detector_pepper.py

import socket
import struct
import numpy as np
import time
from naoqi import ALProxy

PEPPER_IP = "192.168.0.109"
PORT = 9559

# === Pepper Video Setup ===
resolution = 3 #2 # VGA (640x480)
color_space = 13 #11  # RGB
fps = 30  #5

video = ALProxy("ALVideoDevice", PEPPER_IP, PORT)
motion = ALProxy("ALMotion", PEPPER_IP, PORT)

# === Socket Setup ===
PC_IP = '192.168.0.101'  # Replace with your PC's IP
VIDEO_PORT = 5006
CMD_PORT = 5007

video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
video_socket.connect((PC_IP, VIDEO_PORT))

cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cmd_socket.connect((PC_IP, CMD_PORT))

subscriber_id = video.subscribeCamera("pepper_stream", 0, resolution, color_space, fps)

def perform_gesture(gesture):
    print("Executing gesture:", gesture)
    if gesture == "wave":
        motion.setAngles(["RShoulderPitch", "RElbowYaw", "RElbowRoll"], [1.0, 1.5, 1.0], 0.2)
    elif gesture == "point":
        motion.setAngles(["RShoulderPitch", "RElbowRoll"], [1.0, 1.5], 0.2)
    elif gesture == "raise_left_arm":
        motion.setAngles(["LShoulderPitch", "LElbowRoll"], [0.5, -1.0], 0.2)
    elif gesture == "raise_right_arm":
        motion.setAngles(["RShoulderPitch", "RElbowRoll"], [0.5, 1.0], 0.2)
    elif gesture == "raise_both_arms":
        motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.2)
    elif gesture == "peace_sign":
        motion.setAngles(["RShoulderPitch", "RElbowYaw", "RElbowRoll"], [1.0, 1.0, 0.8], 0.2)

try:
    while True:
        # === 1. Send camera frame ===
        img = video.getImageRemote(subscriber_id)
        if img:
            width, height, array = img[0], img[1], img[6]
            frame = np.frombuffer(bytearray(array), dtype=np.uint8).reshape((height, width, 3))
            data = frame.tobytes()
            video_socket.sendall(struct.pack("L", len(data)) + data)

        # === 2. Receive gesture command ===
        try:
            cmd = cmd_socket.recv(1024).decode().strip()
            if cmd:
                perform_gesture(cmd)
        except socket.error:
            pass

        time.sleep(0.1)

finally:
    video.unsubscribe(subscriber_id)
    video_socket.close()
    cmd_socket.close()

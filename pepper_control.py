#! /usr/bin/python2

import socket
import struct
import numpy as np
from naoqi import ALProxy

# Pepper's IP and Port
PEPPER_IP = "192.168.0.109"  # Pepper IP
PORT = 9559

'''PARAMETERS'''
# Subscribe to the video feed
resolution = 3              # 1280x960
color_space = 13            # BGR color space
fps = 30                    # max fos = 30

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

# Create proxy
'''
Everything you need from the NAOqi should be defined here. I just imported some basic proxies
'''
video_service = ALProxy("ALVideoDevice", PEPPER_IP, PORT)
posture = ALProxy("ALRobotPosture", PEPPER_IP, PORT)
behavior = ALProxy("ALBehaviorManager", PEPPER_IP, PORT)
touch = ALProxy("ALTouch", PEPPER_IP, PORT)
speech_recognition = ALProxy("ALSpeechRecognition", PEPPER_IP, PORT)
motion = ALProxy("ALMotion", PEPPER_IP, PORT)
audio = ALProxy("ALAudioSourceLocalization", PEPPER_IP, PORT)

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
    speech_recognition.setLanguage("English")

    vocabulary = ["Come here Pepper"]
    speech_recognition.setVocabulary(vocabulary, False) 
    speech_recognition.subscribe("PepperCommand")
    print("Listening for 'Come here Pepper'...")

    detected = False
    start_time = time.time()

    while time.time() - start_time < 20:
        localization_result = audio.getEstimatedSource()

        if localization_result:
            azimuth = localization_result[0]
            print(f"Sound detected at angle {azimuth]")

            detected_word = speech_recognition.getRecognitionConfidence()
            if detected_word:
                print("Recognised 'Come here Pepper' and moving toward sound...")

                motion.moveTo(0,0,azimuth)
                motion.moveTo(0.5, 0, 0)
                detected - True
                break

        time.sleep(1)

    speech_recognition.unsubscribe("PepperCommand")

    if not detected:
        print("Did not here command in time")
        
    #print("Being summoned...")
    #pepper_tts("On my way")

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
        subscriber_id = video_service.subscribeCamera("pepper_stream", 0, resolution, color_space, fps)
        image_container = video_service.getImageRemote(subscriber_id)

        while True:
            if image_container:
                width, height = image_container[0], image_container[1]
                array = image_container[6]
                frame = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))

                # Send frame size and data
                conn_vid.sendall(struct.pack("L", len(frame.tobytes())) + frame.tobytes())
            data = conn_con.recv(1024).decode()
            if not data:
                break


            if data == 'c':
                pepper_call()

            elif data == 'z':
                pepper_raiseArm()

            elif data == 'f':
                pepper_sing()

            elif data == '1':
                pepper_summon()

    finally:
        video_service.unsubscribe(subscriber_id)
        conn_vid.close()
        conn_con.close()
        server_socket_vid.close()
        server_socket_con.close()

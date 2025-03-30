#! /usr/bin/python2

import socket
import struct
import numpy as np
import qi
import time
from naoqi import ALProxy
import time
import argparse

# Pepper's IP and Port
PEPPER_IP = "192.168.0.119"  # Pepper IP
PORT = 9559

'''PARAMETERS'''
# Subscribe to the video feed
resolution = 3              # 1280x960
color_space = 13            # BGR color space
fps = 10                    # max fos = 30
parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, default=PEPPER_IP,
                    help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
parser.add_argument("--port", type=int, default=9559,
                    help="Naoqi port number")

args = parser.parse_args()
session = qi.Session()

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

# Create proxy
'''
Everything you need from the NAOqi should be defined here. I just imported some basic proxies
'''
video_service = ALProxy("ALVideoRecorder", PEPPER_IP, PORT)
posture = ALProxy("ALRobotPosture", PEPPER_IP, PORT)
behavior = ALProxy("ALBehaviorManager", PEPPER_IP, PORT)
touch = ALProxy("ALTouch", PEPPER_IP, PORT)
speech_recognition = ALProxy("ALSpeechRecognition", PEPPER_IP, PORT)
motion = ALProxy("ALMotion", PEPPER_IP, PORT)
audio = ALProxy("ALSoundLocalization", PEPPER_IP, PORT)
memory = ALProxy("ALMemory", PEPPER_IP, PORT)
tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)
photoCaptureProxy = ALProxy("ALPhotoCapture", PEPPER_IP, PORT)
tablet = ALProxy("ALTabletService", PEPPER_IP, PORT)

def pepper_tts(word):
    print("TTS started...")
    tts.say(word)

def pepper_tabletPrint(word):
    #TODO: Print words onto the tablet
    tablet.showWebview("data:text/html,<html><body><h1>{}</h1></body></html>".format(word))

def pepper_call():
    #TODO: Call someone according to selected contact and display "Calling ${CONTACT}" output onto ipad.
    print("Select call contact")
    while (not data):
        data = conn_con.recv(1024).decode()
    
        if data:
            if (data == '1'):
                print("Calling contact 1")
                pepper_tabletPrint("Calling contact 1")
                pepper_tts("Calling contact 1")
                # Contact 1
            elif (data == '2'):
                print("Calling contact 2")
                pepper_tabletPrint("Calling contact 2")
                pepper_tts("Calling contact 2")
                # Contact 2
            elif (data == '3'):
                print("Calling contact 3")
                pepper_tabletPrint("Calling contact 3")
                pepper_tts("Calling contact 3")
                # Contact 3

def pepper_raiseArm():
    motion = ALProxy("ALMotion", PEPPER_IP, PORT)
    posture = ALProxy("ALRobotPosture", PEPPER_IP, PORT)

    # Wake up robot
    motion.wakeUp()

    # Raise right arm
    joint_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
    raise_angles = [0.0, -0.5, 1.5, 1.0]  # Friendly outward arm raise
    speed = 0.2

    print("Raising arm...")
    motion.setAngles(joint_names, raise_angles, speed)
    pepper_tts("Hi, I'm raising my arm!")

    # Hold for 2 seconds
    sleep(2)

    # Lower arm back down
    lower_angles = [1.5, 0.2, 1.2, 0.5]  # Relaxed natural posture
    print("Lowering arm...")
    motion.setAngles(joint_names, lower_angles, speed)

def call_j_person():
    print("Who would you like to call? Mum, Dad, or Police?")
    speech_recognition.setVocabulary(["Mum", "Dad", "Police"], False)
    speech_recognition.subscribe("Call_J_Person")
    
    start_time = time.time()
    detected = False
    while time.time() - start_time < 10:  # Listen for 10 seconds
        phrase_data = memory.getData("WordRecognized")
        if phrase_data and len(phrase_data) > 1:
            recognised_phrase = phrase_data[0]
            confidence = phrase_data[1]
        else:
            recognised_phrase = ""
            confidence = 0.0
        
        if recognised_phrase in ["Mum", "Dad", "Police"] and confidence > 0.5:
            print("Calling {}...".format(recognised_phrase))
            pepper_tabletPrint("Calling {}...".format(recognised_phrase))
            
            speech_recognition.unsubscribe("Call_J_Person")
            return recognised_phrase
        
        time.sleep(0.5)
    
    speech_recognition.unsubscribe("Call_J_Person")
    print("I don't understand. Please try again.")
    pepper_tabletPrint("I don't understand. Please try again.")
    return None
    

def pepper_sing():
    #TODO: Sing
    print("Singing...")
    pepper_tabletPrint("Singing...")

# Path to the MP3 file you uploaded to Pepper
    mp3_file_path = "/home/nao/Pepper_song.mp3"  # Adjust the path based on where the file is uploaded

    # Create the ALAudioPlayer proxy
    try:
        audio_player = ALProxy("ALAudioPlayer", PEPPER_IP, PORT)

        # Load and play the MP3 file
        audio_player.load(mp3_file_path)
        audio_player.playFile(mp3_file_path)

        print(f"Playing {mp3_file_path}")
        pepper_tts("Now I am playing the song!")
        pepper_tabletPrint("Now I am playing the song!")

    except Exception as e:
        print(f"Error playing MP3 file: {e}")
        pepper_tts("Sorry, I couldn't play the song.")
        pepper_tabletPrint("Sorry, I couldn't play the song.")

def set_pose_for_sensor(sensor_name, motion):
    names = list()
    times = list()
    keys = list()
    
    if "Head" in sensor_name:
        #BSL sign for thank you/please
        names.append("RElbowRoll")
        times.append([0.44, 0.96, 1.24])
        keys.append([[1.39975, [3, -0.16, 0], [3, 0.173333, 0]], [0.00872665, [3, -0.173333, 0], [3, 0.0933333, 0]], [0.44855, [3, -0.0933333, 0], [3, 0, 0]]])

        names.append("RElbowYaw")
        times.append([0.44, 1.24])
        keys.append([[0.705113, [3, -0.16, 0], [3, 0.266667, 0]], [-0.548033, [3, -0.266667, 0], [3, 0, 0]]])

        names.append("RHand")
        times.append([0.44])
        keys.append([[0.98, [3, -0.16, 0], [3, 0, 0]]])

        names.append("RShoulderPitch")
        times.append([0.44, 0.96, 1.24, 1.44])
        keys.append([[-2.0, [3, -0.16, 0], [3, 0.173333, 0]], [0.214268, [3, -0.173333, -0.0737064], [3, 0.0933333, 0.0396881]], [0.366363, [3, -0.0933333, -0.0733103], [3, 0.0666667, 0.0523645]], [0.591293, [3, -0.0666667, 0], [3, 0, 0]]])

        names.append("RShoulderRoll")
        times.append([0.44])
        keys.append([[-1.0, [3, -0.16, 0], [3, 0, 0]]])

        names.append("RWristYaw")
        times.append([0.04, 0.44])
        keys.append([[1.25489, [3, -0.0266667, 0], [3, 0.133333, 0]], [1.27584, [3, -0.133333, 0], [3, 0, 0]]])

    elif "HandLeft" in sensor_name:
        #test movement for left hand
        names.append("RShoulderPitch")
        times.append([0.5, 1.0])
        keys.append([[1.85878, [3, -0.133333, 0], [3, 0, 0]], [1.85878, [3, -0.133333, 0], [3, 0, 0]]])

    elif "HandRight" in sensor_name:
        #test movement for right hand
        names.append("RShoulderRoll")
        times.append([0.5, 1.0])
        keys.append([[0.7375, [3, -0.133333, 0], [3, 0, 0]], [-1.0, [3, -0.133333, 0], [3, 0, 0]]])

    elif "Bumper" in sensor_name:    
        #test movement for bumper
        names.append("RWristYaw")
        times.append([0.5, 1.0])
        keys.append([[-1.73835, [3, -0.133333, 0], [3, 0, 0]], [0, [3, -0.133333, 0], [3, 0, 0]]])

    #verifying before execution
    print("Names: {}".format(names))
    print("Times: {}".format(times))
    print("Keys: {}".format(keys))

    #execute the motion
    if names and times and keys:
        try:
            motion.angleInterpolationBezier(names, times, keys)
            print("Motion executed successfully!")
            pepper_tabletPrint("Motion executed successfully!")
        except Exception as e:
            print("Error executing motion: {}".format(e))
            pepper_tabletPrint("Error executing motion: {}".format(e))

def pepper_checkTouch(touch, tts, motion):
    motion.wakeUp()
    posture.goToPosture("Stand", 0.5)
    print("Checking for touch...")
    pepper_tabletPrint("Checking for touch...")
    touched_sensors = touch.getStatus()  #getting the touch sensor status
    
    for sensor in touched_sensors:
        sensor_name = sensor[0]  #name of the sensor
        is_touched = sensor[1]  #1 if touched, 0 if not
        
        if is_touched:
            print("Try touching one of my sensors and I'll perform a BSL sign!")
            tts.say("Try touching one of my sensors and I'll perform a BSL sign!")
            pepper_tabletPrint("Try touching one of my sensors and I'll perform a BSL sign!")

            #do particular motion for sensor touched
            set_pose_for_sensor(sensor_name, motion)

            #explain that head sensor touched and what is being signed
            if "Head" in sensor_name:
                print("Head sensor touched: performing BSL sign for 'Thank you'/'Please'...")
                tts.say("Head sensor touched: performing BSL sign for 'Thank you'/'Please'...")
                pepper_tabletPrint("Head sensor touched: performing BSL sign for 'Thank you'/'Please'...")
            elif "HandLeft" in sensor_name:
                print("Hand left sensor touched!")
                tts.say("Hand left sensor touched!")
                pepper_tabletPrint("Hand left sensor touched!")
            elif "HandRight" in sensor_name:
                print("Hand right sensor touched!")
                tts.say("Hand right sensor touched!")
                pepper_tabletPrint("Hand right sensor touched!")
            elif "Bumper" in sensor_name:
                print("Bumper sensor touched!)
                tts.say("Bumper sensor touched!")
                pepper_tabletPrint("Bumper sensor touched!")
              
if __name__=="__main__":
    try:
        # Get video feed and send to process.py
        pepper_tts("Hello, this is Pepper. Your BSL recognition companion")
        pepper_tabletPrint("Hello, this is Pepper. Your BSL recognition companion")
        
        session.connect("tcp://" + args.ip + ":" + str(args.port))

        print("Connected to Pepper!")
        vid_recorder_service = session.service("ALVideoRecorder")

        vid_recorder_service.setResolution(2)
        vid_recorder_service.setFrameRate(10)
        vid_recorder_service.setVideoFormat("MJPG")
        vid_recorder_service.startRecording("/home/nao/recordings/cameras", "k9do")

        time.sleep(20)

        videoInfo = vid_recorder_service.stopRecording()

        print("Video was saved on the robot: ", videoInfo[1])
        print("Num frames: ", videoInfo[0])
        while True:
            pepper_checkTouch()
            data = conn_con.recv(1024).decode()
            if not data:
                time.sleep(1)
                continue


            if data == 'c':
                pepper_call()

            elif data == 'z':
                pepper_raiseArm()

            elif data == 'f':
                pepper_sing()

            time.sleep(1)


    finally:

        server_socket_con.close()

#! /usr/bin/python2

import socket
import struct
import numpy as np
import time
from naoqi import ALProxy
from time import sleep

# Pepper's IP and Port
PEPPER_IP = "192.168.0.109"  # Pepper IP
PORT = 9559

'''PARAMETERS'''
# Subscribe to the video feed
resolution = 3              # 1280x960
color_space = 13            # BGR color space
fps = 10                    # max fos = 30

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
audio = ALProxy("ALSoundLocalization", PEPPER_IP, PORT)
memory = ALProxy("ALMemory", PEPPER_IP, PORT)

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
            speech_recognition.unsubscribe("Call_J_Person")
            return recognised_phrase
        
        time.sleep(0.5)
    
    speech_recognition.unsubscribe("Call_J_Person")
    print("I don't understand. Please try again.")
    return None
    

def pepper_sing():
    #TODO: Sing
    print("Singing...")

def pepper_summon():
    #TODO: Pepper respond to the call of its name, and move towards user
        speech_recognition.setLanguage("English") #sets recognised language as English
        vocabulary = ["Come here Pepper"] #setting vocabulary as the phrase 'come here pepper'
        speech_recognition.setVocabulary(vocabulary, False)  #"False" here turns off wordspotting
        speech_recognition.subscribe("Summoning_Pepper") #subscribing to the ALSpeechRecognition module
        print("Listening for 'Come here Pepper'...")
    
        detected = False
        start_time = time.time() #start timer assuming no sound is detected

        while time.time() - start_time < 20: 
            localise_sound = audio.getEstimatedSource()
            if localise_sound:
                azimuth = localise_sound[0] #finding the direction of the sound using the ALAudioSourceLocalization module
                print("Sound detected at angle {}".format(azimuth)) 

                phrase_data = memory.getData("WordRecognized")
                if phrase_data and len(phrase_data) >1:
                    recognised_phrase = phrase_data[0]
                    confidence = phrase_data[1]
                    
                else: 
                    recognised_phrase = ""
                    confidence = 0.0 #setting default values
                    
                if "Come here Pepper" in recognised_phrase and confidence >0.5: #pepper moves towards the sound if phrase detected and confidence is high
                    print("Recognised 'Come here Pepper'! On my way...")
                    pepper_tts("Recognised 'Come here Pepper'! On my way...")

                    motion.moveTo(0, 0, np.deg2rad(azimuth)) #converting from degrees to radians, and pepper changing to face that direction
                    motion.moveTo(1.0, 0, 0) #move 1.0 metre towards the sound

                    while True:
                        obstacle_front = memory.getData("Device/SubDeviceList/US/Front/Sensor/Value")#checking if obstacle in front of pepper using front sonar sensor
                        if obstacle_front < 0.6: #checking if an obstacle is detected within 0.6 metres
                            print("I detected an obstacle, so I am stopping here...")
                            pepper_tts("I detected an obstacle so I am stopping here")
                            motion.stopMove()
                            break
                        time.sleep(0.5)
                    detected = True
                    break
            time.sleep(0.5)
        speech_recognition.unsubscribe("Summoning_Pepper")

        if not detected:
            print("I'm sorry, I did not hear 'Come here Pepper'")
            pepper_tts("I'm sorry, I did not hear 'Come here Pepper'")

def set_pose_for_sensor(sensor_name, motion):
    names = list()
    times = list()
    keys = list()
    
    if "Head" in sensor_name:
        #BSL sign for thank you/please
        names.append("RShoulderPitch")
        times.append([0.5, 1.0])
        keys.append([[1.85878, [3, -0.133333, 0], [3, 0, 0]],
                    [1.85878, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RElbowRoll")
        times.append([0.5, 1.0])
        keys.append([[0.98262, [3, -0.133333, 0], [3, 0, 0]],
                    [0.98262, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RShoulderRoll")
        times.append([0.5, 1.0])
        keys.append([[0.7375, [3, -0.133333, 0], [3, 0, 0]],
                    [0.7375, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RElbowYaw")
        times.append([0.5, 1.0])
        keys.append([[-0.663225, [3, -0.133333, 0], [3, 0, 0]],
                    [0, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RWristYaw")
        times.append([0.5, 1.0])
        keys.append([[-1.73835, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RHand")
        times.append([0.5, 1.0])
        keys.append([[0.67, [3, -0.133333, 0], [3, 0, 0]],
                    [0.67, [3, -0.133333, 0], [3, 0, 0]]])

    elif "HandLeft" in sensor_name:
        #test movement
        names.append("RShoulderPitch")
        times.append([0.5, 1.0])
        keys.append([[1.85878, [3, -0.133333, 0], [3, 0, 0]],
                    [1.85878, [3, -0.133333, 0], [3, 0, 0]]])

    elif "HandRight" in sensor_name:
        #test movement
        names.append("RShoulderRoll")
        times.append([0.5, 1.0])
        keys.append([[0.7375, [3, -0.133333, 0], [3, 0, 0]],
                    [-1.0, [3, -0.133333, 0], [3, 0, 0]]])


    elif "Bumper" in sensor_name:    
        #test movement
        names.append("RWristYaw")
        times.append([0.5, 1.0])
        keys.append([[-1.73835, [3, -0.133333, 0], [3, 0, 0]],
                    [0, [3, -0.133333, 0], [3, 0, 0]]])


    if names:
        motion.angleInterpolationBezier(names, times, keys)

def pepper_checkTouch(touch, tts, motion):
    print("Checking for touch...")
    touched_sensors = touch.getStatus()  # Getting the touch sensor status
    
    for sensor in touched_sensors:
        sensor_name = sensor[0]  # name of the sensor
        is_touched = sensor[1]  # 1 if touched, 0 if not
        
        if is_touched:
            print("Try touching one of my sensors and I'll perform a BSL sign!")
            tts.say("Try touching one of my sensors and I'll perform a BSL sign!") 

            # do particular motion for sensor touched
            set_pose_for_sensor(sensor_name, motion)

            # explain that head sensor touched and what is being signed
            if "Head" in sensor_name:
                print("Head sensor touched: performing BSL sign for 'Thank you'/'Please'...")
                tts.say("Head sensor touched: performing BSL sign for 'Thank you'/'Please'...")
            elif "HandLeft" in sensor_name:
                tts.say("hand left")
            elif "HandRight" in sensor_name:
                tts.say("hand right")
            elif "Bumper" in sensor_name:
                tts.say("bumper")

if __name__=="__main__":
    try:
        # Get video feed and send to process.py
        subscriber_id = video_service.subscribeCamera("pepper_stream", 0, resolution, color_space, fps)

        while True:
            image_container = video_service.getImageRemote(subscriber_id)
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
            elif data == '3':

            elif data == 'N/a':
                call_j_person()
        
                #not sure how to call functions here

    finally:
        video_service.unsubscribe(subscriber_id)
        conn_vid.close()
        conn_con.close()
        server_socket_vid.close()
        server_socket_con.close()

# -*- coding: utf-8 -*-
from naoqi import ALProxy
import time

PEPPER_IP = "192.168.1.100"  # 
PORT = 9559

# 
faceDetect = ALProxy("ALFaceDetection", PEPPER_IP, PORT)
faceChar = ALProxy("ALFaceCharacteristics", PEPPER_IP, PORT)
tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)

# 
faceDetect.subscribe("EmotionSinger")
print(" Looking for face...")

face_id = None
start_time = time.time()
timeout = 10  # seconds

while time.time() - start_time < timeout:
    face_data = faceDetect.getFaces()
    if face_data and len(face_data) > 0:
        face_id = face_data[0][0]  
        print("Face detected with ID:", face_id)
        break
    time.sleep(0.5)

if face_id:
  
    faceChar.analyzeFaceCharacteristics(face_id)
    time.sleep(0.5)

    try:
        props = faceChar.getExpressionProperties(face_id)
        emotions = ["neutral", "happy", "surprised", "angry", "sad"]
        emotion_index = props.index(max(props))
        emotion = emotions[emotion_index]
        print("Detected emotion:", emotion)

        
        tts.setParameter("pitchShift", 1.2)
        tts.setParameter("speed", 70)

        if emotion == "happy":
            tts.say("\\vct=130\\ \\rspd=70\\ If you're happy and you know it, clap your hands!")
        elif emotion == "sad":
            tts.say("\\vct=100\\ \\rspd=60\\ It's okay to cry, tomorrow is a new day.")
        elif emotion == "angry":
            tts.say("\\vct=110\\ \\rspd=65\\ Breathe in, breathe out, let the anger go.")
        elif emotion == "surprised":
            tts.say("\\vct=140\\ \\rspd=75\\ Oh wow! What just happened!")
        elif emotion == "neutral":
            tts.say("\\vct=120\\ \\rspd=70\\ Hello there! Nice to meet you.")
    except Exception as e:
        print("Error reading expression:", e)
        tts.say("I saw you, but I couldn't read your emotion.")
else:
    print("No face found.")
    tts.say("I don't see anyone to sing to.")


faceDetect.unsubscribe("EmotionSinger")

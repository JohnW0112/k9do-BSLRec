
from naoqi import ALProxy
import time

# Pepper IP and Port
PEPPER_IP = "192.168.1.100"  # change to your robot's IP
PORT = 9559

# Create proxies
faceC = ALProxy("ALFaceCharacteristics", PEPPER_IP, PORT)
memory = ALProxy("ALMemory", PEPPER_IP, PORT)
tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)

# Emotion thresholds
confidence = 0.5
emotion_list = ["neutral", "happy", "surprised", "angry", "sad"]
emotion_scores = [0, 0, 0, 0, 0]
count = 0

print("Detecting emotion...")

while count < 4:
    try:
        ids = memory.getData("PeoplePerception/PeopleList")
        if not ids or len(ids) == 0:
            print("No face detected.")
            break
        elif len(ids) > 1:
            print("Multiple faces detected.")
            break
        else:
            faceC.analyzeFaceCharacteristics(ids[0])
            time.sleep(0.2)
            values = memory.getData("PeoplePerception/Person/" + str(ids[0]) + "/ExpressionProperties")
            for i in range(5):
                emotion_scores[i] += values[i]
            count += 1
    except:
        continue

# Compute average
if count == 4:
    emotion_scores = [v / 4.0 for v in emotion_scores]
    max_score = max(emotion_scores)
    if max_score > confidence:
        emotion = emotion_list[emotion_scores.index(max_score)]
        print("Detected emotion:", emotion)

        # Say song based on emotion
        tts.setParameter("pitchShift", 1.2)
        tts.setParameter("speed", 70)

        if emotion == "happy":
            tts.say("\\vct=130\\ \\rspd=70\\ If you're happy and you know it, clap your hands!")
        elif emotion == "sad":
            tts.say("\\vct=100\\ \\rspd=60\\ It's okay to cry, the sun will shine again...")
        elif emotion == "angry":
            tts.say("\\vct=110\\ \\rspd=65\\ Take a deep breath, count to three, let it go...")
        elif emotion == "surprised":
            tts.say("\\vct=140\\ \\rspd=75\\ Oh wow! Life is full of wonder and surprise!")
        elif emotion == "neutral":
            tts.say("\\vct=120\\ \\rspd=70\\ Hello there! Nice to meet you.")
    else:
        print("No strong emotion detected.")
else:
    print("Not enough data.")

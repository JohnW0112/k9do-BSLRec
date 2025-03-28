# -*- coding: utf-8 -*-
from naoqi import ALProxy
import time

PEPPER_IP = "192.168.0.109"
PORT = 9559

# Create proxies
tts = ALProxy("ALTextToSpeech", PEPPER_IP, PORT)
animated_speech = ALProxy("ALAnimatedSpeech", PEPPER_IP, PORT)
tablet = ALProxy("ALTabletService", PEPPER_IP, PORT)
face_detect = ALProxy("ALFaceDetection", PEPPER_IP, PORT)
face_char = ALProxy("ALFaceCharacteristics", PEPPER_IP, PORT)

def pepper_ipadPrint(text):
    """Display text on Pepper's tablet."""
    tablet.executeJS("document.body.innerHTML = '<h1 style=\"font-size:40px; text-align:center;\">{}</h1>';".format(text))
    print("Displaying on tablet:", text)

def detect_emotion():
    """Detect emotion with stabilized face and multiple expression checks."""
    face_detect.subscribe("EmotionApp")
    print(" Looking for a stable face...")

    stable_face_id = None
    stable_count = 0

    # Step 1: Wait until a stable face is detected
    for _ in range(20):  # up to ~10 seconds
        faces = face_detect.getFaces()
        if faces:
            current_id = faces[0][0]
            if current_id == stable_face_id:
                stable_count += 1
            else:
                stable_face_id = current_id
                stable_count = 1

            if stable_count >= 3:
                print(" Stable face detected:", stable_face_id)
                break
        time.sleep(0.3)

    face_detect.unsubscribe("EmotionApp")

    if stable_count < 3:
        print(" No stable face detected.")
        return None

    # Step 2: Analyze expression multiple times
    emotion_scores = [0, 0, 0, 0, 0]  # neutral, happy, surprised, angry, sad
    emotions = ["neutral", "happy", "surprised", "angry", "sad"]
    checks = 5

    for _ in range(checks):
        try:
            face_char.analyzeFaceCharacteristics(stable_face_id)
            time.sleep(0.3)
            props = face_char.getExpressionProperties(stable_face_id)
            for i in range(5):
                emotion_scores[i] += props[i]
        except Exception as e:
            print("⚠️ Error analyzing:", e)

    # Step 3: Average and thresholding
    emotion_scores = [v / float(checks) for v in emotion_scores]
    max_score = max(emotion_scores)

    print("Emotion scores:", dict(zip(emotions, emotion_scores)))

    if max_score < 0.3:
        print(" Low confidence, fallback to neutral.")
        return "neutral"

    detected_emotion = emotions[emotion_scores.index(max_score)]
    print(" Final detected emotion:", detected_emotion)
    return detected_emotion

def pepper_sing(emotion):
    """Make Pepper sing based on detected emotion."""
    if not emotion:
        emotion = "neutral"

    print("Singing for emotion:", emotion)
    lyrics = ""

    if emotion == "happy":
        lyrics = "\\rspd=70\\ If you're happy and you know it, clap your hands!"
    elif emotion == "sad":
        lyrics = "\\rspd=65\\ It's okay to feel sad sometimes, the sun will shine again."
    elif emotion == "angry":
        lyrics = "\\rspd=65\\ Let's take a deep breath... and let it go..."
    elif emotion == "surprised":
        lyrics = "\\rspd=75\\ Oh my! You look surprised! Life is full of wonder!"
    elif emotion == "neutral":
        lyrics = "\\rspd=70\\ Just a little song to say hello to you."

    pepper_ipadPrint("Emotion: " + emotion + "<br>" + lyrics.replace("\\rspd=70\\", "").replace("\\rspd=65\\", ""))
    animated_speech.say(lyrics)
    tts.say("I hope you liked my emotion song!")

if __name__ == "__main__":
    emotion = detect_emotion()
    pepper_sing(emotion)

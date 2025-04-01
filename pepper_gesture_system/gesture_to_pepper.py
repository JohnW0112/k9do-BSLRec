import cv2
import mediapipe as mp
import socket
import time

# Setup socket
UDP_IP = "127.0.0.1"
UDP_PORT = 5002
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("[Init] Socket ready on", UDP_IP, "port", UDP_PORT)

# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
print("[Init] MediaPipe Hands module loaded")

# Utility functions for simple gesture classification
def count_extended_fingers(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    extended = 0
    for tip_id in tips_ids[1:]:  # Skip thumb for now
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            extended += 1
    print("[Debug] Extended fingers:", extended)
    return extended

def classify_gesture(landmarks):
    extended = count_extended_fingers(landmarks)
    thumb_tip = landmarks.landmark[4]
    index_tip = landmarks.landmark[8]

    if extended == 2:
        print("[Debug] Gesture classified as: peace")
        return "peace"  # Peace as closed hand (can adjust)
    elif extended == 1:
        print("[Debug] Gesture classified as: point")
        return "point"
    elif extended >= 4:
        print("[Debug] Gesture classified as: wave")
        return "wave"
    else:
        print("[Debug] Gesture unrecognized")
        return None

# Start webcam feed
cap = cv2.VideoCapture(0)
prev_gesture = None
last_sent_time = 0

print("[Info] Starting webcam feed...")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("[Warning] Camera frame not read successfully")
        continue

    # Flip and convert to RGB
    image = cv2.flip(image, 1)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            gesture = classify_gesture(hand_landmarks)
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Send only if new gesture or after a pause
            if gesture and (gesture != prev_gesture or time.time() - last_sent_time > 2):
                print("[Send] Detected gesture:", gesture)
                sock.sendto(gesture.encode(), (UDP_IP, UDP_PORT))
                print("[Send] Sent to", UDP_IP, ":", UDP_PORT)
                prev_gesture = gesture
                last_sent_time = time.time()

    cv2.imshow("Gesture Recognition", image)
    if cv2.waitKey(5) & 0xFF == 27:
        print("[Exit] Escape key pressed. Exiting...")
        break

cap.release()
print("[Exit] Webcam feed stopped.")

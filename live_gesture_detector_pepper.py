#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

#counter part is pepper_socket_streamer.py

#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import socket
import struct
import cv2
import numpy as np
import mediapipe as mp

# === MediaPipe setup ===
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
pose = mp_pose.Pose()
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

# === Networking ===
VIDEO_PORT = 5006
CMD_PORT = 5007

def fingers_status(hand_landmarks):
    finger_states = []
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    finger_states.append(thumb_tip.x > thumb_ip.x)
    tip_ids = [8, 12, 16, 20]
    pip_ids = [6, 10, 14, 18]
    for tip, pip in zip(tip_ids, pip_ids):
        finger_states.append(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y)
    return finger_states

def detect_gestures(image):
    gestures = []
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pose_result = pose.process(image_rgb)
    hands_result = hands.process(image_rgb)

    h, w, _ = image.shape
    hand_label_map = {}

    if pose_result.pose_landmarks:
        landmarks = pose_result.pose_landmarks.landmark
        lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        if lw.y < ls.y and rw.y < rs.y:
            gestures.append("raise_both_arms")
        elif lw.y < ls.y:
            gestures.append("raise_left_arm")
        elif rw.y < rs.y:
            gestures.append("raise_right_arm")
        mp_draw.draw_landmarks(image, pose_result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    if hands_result.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(hands_result.multi_hand_landmarks):
            hand_type = hands_result.multi_handedness[i].classification[0].label
            hand_label_map[hand_type] = hand_landmarks
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if "Right" in hand_label_map:
            rh = hand_label_map["Right"]
            status = fingers_status(rh)
            hand_y = (rh.landmark[0].y + rh.landmark[5].y) / 2
            if sum(status[1:]) == 5 and hand_y < 0.5:
                gestures.append("wave")
            if status[1] and not any(status[2:]):
                gestures.append("point")
            if status[1] and status[2] and not any(status[3:]):
                gestures.append("peace_sign")
        if "Left" in hand_label_map:
            lh = hand_label_map["Left"]
            status = fingers_status(lh)
            if status[1] and status[2] and not any(status[3:]):
                gestures.append("peace_sign")

    return list(set(gestures)), image

# === Start sockets ===
video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
video_sock.bind(('', VIDEO_PORT))
video_sock.listen(1)
print("Waiting for Pepper video stream...")
video_conn, _ = video_sock.accept()
print("Video connected.")

cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cmd_sock.bind(('', CMD_PORT))
cmd_sock.listen(1)
print("Waiting for Pepper gesture control connection...")
cmd_conn, _ = cmd_sock.accept()
print("Command connected.")

last_sent = None
last_valid_gesture = None

while True:
    try:
        payload_size = struct.calcsize("L")
        data = b''
        while len(data) < payload_size:
            data += video_conn.recv(4096)
        packed_msg_size = data[:payload_size]
        msg_size = struct.unpack("L", packed_msg_size)[0]
        data = data[payload_size:]

        while len(data) < msg_size:
            data += video_conn.recv(4096)

        frame_data = data[:msg_size]
        frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((1280, 960, 3))
        gestures, annotated = detect_gestures(frame)

        if gestures:
            gesture = gestures[0]  # pick one to send
            last_valid_gesture = gesture
        else:
            gesture = last_valid_gesture

        if gesture != last_sent and gesture:
            print("Sending gesture:", gesture)
            cmd_conn.sendall((gesture + "\n").encode())
            last_sent = gesture

        cv2.imshow("Pepper Stream (from top camera)", annotated)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    except Exception as e:
        print("Error:", e)
        break

video_conn.close()
cmd_conn.close()

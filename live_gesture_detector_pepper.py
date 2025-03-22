#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

#counter part is pepper_socket_streamer.py

import cv2
import numpy as np
import mediapipe as mp
import qi
import argparse

# === MediaPipe setup ===
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
pose = mp_pose.Pose()
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

def fingers_status(hand_landmarks):
    """Returns a list of which fingers are up: [thumb, index, middle, ring, pinky]"""
    finger_states = []

    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    finger_states.append(thumb_tip.x > thumb_ip.x)

    tip_ids = [8, 12, 16, 20]
    pip_ids = [6, 10, 14, 18]
    for tip, pip in zip(tip_ids, pip_ids):
        finger_states.append(
            hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y
        )

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
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        left_raised = left_wrist.y < left_shoulder.y
        right_raised = right_wrist.y < right_shoulder.y

        if left_raised and right_raised:
            gestures.append("raise_both_arms")
        elif left_raised:
            gestures.append("raise_left_arm")
        elif right_raised:
            gestures.append("raise_right_arm")

        mp_draw.draw_landmarks(image, pose_result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    if hands_result.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(hands_result.multi_hand_landmarks):
            hand_type = hands_result.multi_handedness[i].classification[0].label
            hand_label_map[hand_type] = hand_landmarks
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if "Right" in hand_label_map:
            right_hand = hand_label_map["Right"]
            status = fingers_status(right_hand)
            hand_y = (right_hand.landmark[0].y + right_hand.landmark[5].y) / 2

            if sum(status[1:]) == 5 and hand_y < 0.5:
                gestures.append("wave")
            if status[1] and not any(status[2:]):
                gestures.append("point")
            if status[1] and status[2] and not any(status[3:]):
                gestures.append("peace_sign")

        if "Left" in hand_label_map:
            left_hand = hand_label_map["Left"]
            status = fingers_status(left_hand)
            if status[1] and status[2] and not any(status[3:]):
                gestures.append("peace_sign")

    return list(set(gestures)), image

def main(session):
    # === Pepper camera config ===
    video_service = session.service("ALVideoDevice")
    resolution = 2  # VGA: 640x480
    color_space = 11  # RGB
    fps = 5
    camera_index = 0  # Top camera

    subscriber_id = video_service.subscribeCamera("pepper_gesture_stream", camera_index, resolution, color_space, fps)

    # === Store last valid gestures across frames ===
    last_valid_gestures = []

    try:
        while True:
            nao_image = video_service.getImageRemote(subscriber_id)
            if nao_image is None:
                continue

            width, height = nao_image[0], nao_image[1]
            array = nao_image[6]

            image = np.frombuffer(bytearray(array), dtype=np.uint8).reshape((height, width, 3))

            gestures, visual = detect_gestures(image)

            if gestures:
                last_valid_gestures = gestures
                print("New gestures detected:", gestures)
            else:
                gestures = last_valid_gestures
                print("No new gesture – keeping last:", gestures)

            # Save to gesture_labels.txt
            with open("gesture_labels.txt", "w") as f:
                for g in gestures:
                    f.write(g + "\n")

            # Show live feed with annotations (for debugging)
            cv2.imshow("Pepper Camera Gesture Detection", visual)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        video_service.unsubscribe(subscriber_id)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.0.109")
    parser.add_argument("--port", type=int, default=9559)
    args = parser.parse_args()

    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
        main(session)
    except RuntimeError:
        print("Can't connect to Naoqi at ip \"{}\" on port {}".format(args.ip, args.port))
        exit(1)

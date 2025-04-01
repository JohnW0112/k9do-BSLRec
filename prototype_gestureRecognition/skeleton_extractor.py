import cv2
import numpy as np
import mediapipe as mp

class SkeletonExtractor:
    def __init__(self, static_image_mode=False, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def extract_landmarks(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.holistic.process(image_rgb)

        pose_landmarks = []
        right_hand = []
        left_hand = []

        if results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                pose_landmarks.append([lm.x, lm.y, lm.z, lm.visibility])
        if results.right_hand_landmarks:
            for lm in results.right_hand_landmarks.landmark:
                right_hand.append([lm.x, lm.y, lm.z])
        if results.left_hand_landmarks:
            for lm in results.left_hand_landmarks.landmark:
                left_hand.append([lm.x, lm.y, lm.z])

        return {
            'pose': np.array(pose_landmarks) if pose_landmarks else None,
            'right_hand': np.array(right_hand) if right_hand else None,
            'left_hand': np.array(left_hand) if left_hand else None
        }

    def draw_landmarks(self, frame, results):
        self.mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS)
        self.mp_drawing.draw_landmarks(
            frame, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS)
        self.mp_drawing.draw_landmarks(
            frame, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS)

    def close(self):
        self.holistic.close()


def run_skeleton_extraction(debug_draw=True, show_output=True):
    extractor = SkeletonExtractor()
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Extract skeleton
        skeleton = extractor.extract_landmarks(frame)

        # OPTIONAL: Print output once per frame
        if show_output:
            print("Skeleton Output:")
            for part in skeleton:
                if skeleton[part] is not None:
                    print(f"  {part}: shape = {skeleton[part].shape}")
                else:
                    print(f"  {part}: None")

        # OPTIONAL: Visualize landmarks
        if debug_draw:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = extractor.holistic.process(image_rgb)
            extractor.draw_landmarks(frame, results)

        cv2.imshow("Skeleton Extraction", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    extractor.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_skeleton_extraction(debug_draw=True, show_output=True)

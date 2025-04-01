import os
import time
import numpy as np
from collections import deque
from skeleton_extractor import SkeletonExtractor
from sequence_buffer import SequenceBuffer
import cv2

# ========= CONFIG =========
SEQUENCE_LENGTH = 30
SAVE_DIR = "data"
GESTURE_CLASSES = ['hello', 'yes', 'peace', 'idle']  # Added 'idle'
# ==========================

def normalize_label(label_name):
    """Converts gesture name to class index."""
    if label_name not in GESTURE_CLASSES:
        raise ValueError(f"Unknown label: {label_name}")
    return GESTURE_CLASSES.index(label_name)

def ensure_data_folder():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def get_save_path(label_name):
    existing = [f for f in os.listdir(SAVE_DIR) if f.startswith(label_name)]
    return os.path.join(SAVE_DIR, f"{label_name}_{len(existing)+1:03d}.npz")

def main():
    print("\U0001F4E6 Starting gesture data collection")
    print(f"Available gestures: {GESTURE_CLASSES}")
    print("Press ESC to quit\n")

    extractor = SkeletonExtractor()
    cap = cv2.VideoCapture(0)
    ensure_data_folder()

    while True:
        label_name = input("Enter gesture name (or 'exit' to quit): ").strip().lower()
        if label_name == "exit":
            break
        if label_name not in GESTURE_CLASSES:
            print(f"\u274C '{label_name}' not in gesture list. Try again.")
            continue

        buffer = SequenceBuffer(max_length=SEQUENCE_LENGTH)
        print(f"\n\U0001F552 Get ready to perform '{label_name}' in 3 seconds...")
        time.sleep(3)
        print("\u23FA️ Recording now!")

        collected_frames = 0
        while collected_frames < SEQUENCE_LENGTH:
            ret, frame = cap.read()
            if not ret:
                continue

            skeleton = extractor.extract_landmarks(frame)
            buffer.append(skeleton)
            collected_frames += 1

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = extractor.holistic.process(image_rgb)
            extractor.draw_landmarks(frame, results)

            cv2.putText(frame, f"Recording: {label_name} ({collected_frames}/{SEQUENCE_LENGTH})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Recording", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                print("\u274C Interrupted. Skipping this recording.")
                buffer.clear()
                break

        if buffer.is_full():
            sequence = buffer.get_sequence(flatten=True)
            label_index = normalize_label(label_name)
            save_path = get_save_path(label_name)
            np.savez(save_path, sequence=sequence, label=label_index)
            print(f"\u2705 Saved gesture to {save_path}\n")

        buffer.clear()

    cap.release()
    extractor.close()
    cv2.destroyAllWindows()
    print("\U0001F389 Done collecting gestures.")

if __name__ == "__main__":
    main()



"""import os
import time
import numpy as np
from collections import deque
from skeleton_extractor import SkeletonExtractor
from sequence_buffer import SequenceBuffer
import cv2

# ========= CONFIG =========
SEQUENCE_LENGTH = 30
SAVE_DIR = "data"
GESTURE_CLASSES = ['hello', 'yes', 'peace']
# ==========================

def normalize_label(label_name):
    '''Converts gesture name to class index'''
    if label_name not in GESTURE_CLASSES:
        raise ValueError(f"Unknown label: {label_name}")
    return GESTURE_CLASSES.index(label_name)

def ensure_data_folder():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def get_save_path(label_name):
    existing = [f for f in os.listdir(SAVE_DIR) if f.startswith(label_name)]
    return os.path.join(SAVE_DIR, f"{label_name}_{len(existing)+1:03d}.npz")

def main():
    print("📦 Starting gesture data collection")
    print(f"Available gestures: {GESTURE_CLASSES}")
    print("Press ESC to quit\n")

    extractor = SkeletonExtractor()
    cap = cv2.VideoCapture(0)
    ensure_data_folder()

    while True:
        label_name = input("Enter gesture name (or 'exit' to quit): ").strip().lower()
        if label_name == "exit":
            break
        if label_name not in GESTURE_CLASSES:
            print(f"❌ '{label_name}' not in gesture list. Try again.")
            continue

        buffer = SequenceBuffer(max_length=SEQUENCE_LENGTH)
        print(f"\n🕒 Get ready to perform '{label_name}' in 3 seconds...")
        time.sleep(3)
        print("⏺️ Recording now!")

        collected_frames = 0
        while collected_frames < SEQUENCE_LENGTH:
            ret, frame = cap.read()
            if not ret:
                continue

            skeleton = extractor.extract_landmarks(frame)
            buffer.append(skeleton)
            collected_frames += 1

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = extractor.holistic.process(image_rgb)
            extractor.draw_landmarks(frame, results)

            cv2.putText(frame, f"Recording: {label_name} ({collected_frames}/{SEQUENCE_LENGTH})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Recording", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                print("❌ Interrupted. Skipping this recording.")
                buffer.clear()
                break

        if buffer.is_full():
            sequence = buffer.get_sequence(flatten=True)
            label_index = normalize_label(label_name)
            save_path = get_save_path(label_name)
            np.savez(save_path, sequence=sequence, label=label_index)
            print(f"✅ Saved gesture to {save_path}\n")

        buffer.clear()

    cap.release()
    extractor.close()
    cv2.destroyAllWindows()
    print("🎉 Done collecting gestures.")

if __name__ == "__main__":
    main()"""

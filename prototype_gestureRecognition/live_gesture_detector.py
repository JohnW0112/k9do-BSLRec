import cv2
import torch
import numpy as np
from collections import deque, Counter
from datetime import datetime
import csv

from skeleton_extractor import SkeletonExtractor
from sequence_buffer import SequenceBuffer
from gesture_recognition_model import GestureLSTM, load_model

# --- Configurations ---
SEQUENCE_LENGTH = 30
GESTURE_CLASSES = ['hello', 'yes', 'peace', 'idle']
INTENT_SIGNS = ['hello', 'yes', 'peace']
MODEL_PATH = 'gesture_lstm.pth'
PREDICTION_WINDOW = 5
LOG_FILE = "gesture_log.csv"

def predict_gesture(model, sequence, device):
    model.eval()
    with torch.no_grad():
        sequence_tensor = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0).to(device)
        output = model(sequence_tensor)
        probs = torch.softmax(output, dim=1).cpu().numpy()[0]
        predicted_index = np.argmax(probs)
        return GESTURE_CLASSES[predicted_index], probs[predicted_index]

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = GestureLSTM(input_size=258, hidden_size=128, num_classes=len(GESTURE_CLASSES)).to(device)
    load_model(model, MODEL_PATH)

    extractor = SkeletonExtractor()
    buffer = SequenceBuffer(max_length=SEQUENCE_LENGTH)
    prediction_history = deque(maxlen=PREDICTION_WINDOW)

    cap = cv2.VideoCapture(0)
    interaction_state = False
    last_prediction = 'idle'
    gesture_active = False

    # Set up CSV logging
    log_file = open(LOG_FILE, mode="w", newline="")
    csv_writer = csv.writer(log_file)
    csv_writer.writerow(["Timestamp", "Predicted", "Confidence", "Intent", "Transition"])

    print("🤖 Starting real-time gesture detection... Press ESC to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        skeleton = extractor.extract_landmarks(frame)
        buffer.append(skeleton)

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = extractor.holistic.process(image_rgb)
        extractor.draw_landmarks(frame, results)

        transition = "-"
        if buffer.is_full():
            sequence = buffer.get_sequence(flatten=True)
            predicted_sign, confidence = predict_gesture(model, sequence, device)
            prediction_history.append(predicted_sign)
            most_common_prediction = Counter(prediction_history).most_common(1)[0][0]

            # Detect interaction intent
            is_intent = most_common_prediction in INTENT_SIGNS and confidence > 0.9
            if is_intent and not interaction_state:
                print(f"🟢 Intent detected: {most_common_prediction.upper()}")
                interaction_state = True
            elif not is_intent:
                interaction_state = False

            # Temporal segmentation logic
            if last_prediction == 'idle' and most_common_prediction != 'idle':
                print(f"🔵 Gesture start: {most_common_prediction}")
                gesture_active = True
                transition = "start"
            elif last_prediction != 'idle' and most_common_prediction == 'idle':
                print(f"🔴 Gesture end: {last_prediction}")
                gesture_active = False
                transition = "end"

            last_prediction = most_common_prediction

            # Log entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([timestamp, most_common_prediction, f"{confidence:.2f}", is_intent, transition])

            # Display prediction
            cv2.putText(frame, f"Gesture: {most_common_prediction} ({confidence:.2f})",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0) if is_intent else (255, 255, 255), 2)

        cv2.imshow("Live Gesture Detector", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    cap.release()
    extractor.close()
    cv2.destroyAllWindows()
    log_file.close()
    print("🛑 Detection stopped. Log saved to gesture_log.csv.")

if __name__ == "__main__":
    main()

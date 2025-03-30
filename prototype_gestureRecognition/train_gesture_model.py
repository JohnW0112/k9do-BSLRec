import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from gesture_recognition_model import GestureLSTM, train_model, evaluate_model, save_model

# ========= CONFIG =========
DATA_DIR = 'data'
GESTURE_CLASSES = ['hello', 'yes', 'peace', 'idle']
NUM_CLASSES = len(GESTURE_CLASSES)
INPUT_SIZE = 258
SEQ_LENGTH = 30
BATCH_SIZE = 16
EPOCHS = 80
MODEL_PATH = 'gesture_lstm.pth'
# ==========================

class GestureDataset(Dataset):
    def __init__(self, data_dir):
        self.samples = []
        for fname in os.listdir(data_dir):
            if fname.endswith('.npz'):
                self.samples.append(os.path.join(data_dir, fname))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        data = np.load(self.samples[idx])
        sequence = data['sequence']  # (30, 258)
        label = int(data['label'])   # class index (0 to 9)
        return torch.tensor(sequence, dtype=torch.float32), torch.tensor(label, dtype=torch.long)

def main():
    if not os.path.exists(DATA_DIR):
        print(f"❌ Data folder '{DATA_DIR}' not found.")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = GestureDataset(DATA_DIR)
    if len(dataset) < NUM_CLASSES * 5:
        print("⚠️ Not enough data! Try collecting at least 5+ samples per gesture.")
        return

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    model = GestureLSTM(input_size=INPUT_SIZE, hidden_size=128, num_classes=NUM_CLASSES).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    print(f"📊 Training on {len(dataset)} samples ({train_size} train, {val_size} val)")

    for epoch in range(EPOCHS):
        train_loss = train_model(model, train_loader, criterion, optimizer, device)
        val_acc = evaluate_model(model, val_loader, device)
        print(f"Epoch {epoch+1:02d} | Train Loss: {train_loss:.4f} | Val Acc: {val_acc:.4f}")

    save_model(model, MODEL_PATH)
    print(f"\n✅ Model saved as: {MODEL_PATH}")

if __name__ == "__main__":
    main()

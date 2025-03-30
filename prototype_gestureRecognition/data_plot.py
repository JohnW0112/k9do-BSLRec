import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# === CONFIGURATION ===
CSV_FILE = "gesture_log.csv"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# === LOAD CSV ===
df = pd.read_csv(CSV_FILE, parse_dates=["Timestamp"], date_parser=lambda x: pd.to_datetime(x, format=TIME_FORMAT))

# === PLOT 1: Gesture Over Time ===
plt.figure(figsize=(12, 4))
plt.plot(df["Timestamp"], df["Predicted"], drawstyle="steps-post", marker="o")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.xticks(rotation=45)
plt.title("Predicted Gestures Over Time")
plt.xlabel("Time")
plt.ylabel("Gesture")
plt.grid(True)
plt.tight_layout()
plt.show()

# === PLOT 2: Confidence Over Time ===
plt.figure(figsize=(12, 4))
plt.plot(df["Timestamp"], df["Confidence"].astype(float), label="Confidence", color="blue")
plt.axhline(y=0.9, color="red", linestyle="--", label="Intent Threshold")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.xticks(rotation=45)
plt.ylim(0, 1.05)
plt.title("Gesture Confidence Over Time")
plt.xlabel("Time")
plt.ylabel("Confidence")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === PLOT 3: Intent Detection Timeline ===
plt.figure(figsize=(12, 1.5))
plt.scatter(df["Timestamp"], df["Intent"].astype(bool), c=df["Intent"].astype(bool).map({True: "green", False: "gray"}), s=100)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.yticks([0, 1], ["No Intent", "Intent"])
plt.title("Intent Detection Timeline")
plt.xlabel("Time")
plt.grid(True, axis='x')
plt.tight_layout()
plt.show()

print("✅ Plots generated from gesture_log.csv")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# === Load the CSV ===
df = pd.read_csv("C:\\Users\\steph\\Downloads\\pepper_control\\pepper_log.csv") 

# === Convert Timestamp to datetime format ===
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# === Plot 1: Gesture Frequency Count ===
plt.figure(figsize=(10, 5))
sns.countplot(data=df, x='Gesture', order=df['Gesture'].value_counts().index)
plt.title("Frequency of Detected Gestures")
plt.xlabel("Gesture")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# === Plot 2: Gesture Timeline Over Time ===
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='Timestamp', y='Gesture', marker='o', linestyle='None', hue='Gesture')
plt.title("Timeline of Gesture Execution")
plt.xlabel("Time")
plt.ylabel("Gesture")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# === Plot 3: Status Distribution per Gesture ===
plt.figure(figsize=(10, 5))
sns.countplot(data=df, x='Gesture', hue='Status')
plt.title("Execution Status per Gesture")
plt.xlabel("Gesture")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# === Plot 4: Gesture Success Rate Pie Chart ===
success_data = df[df['Status'] == 'executed']
success_counts = success_data['Gesture'].value_counts()
plt.figure(figsize=(7, 7))
plt.pie(success_counts, labels=success_counts.index, autopct='%1.1f%%', startangle=140)
plt.title("Distribution of Successfully Executed Gestures")
plt.tight_layout()
plt.show()

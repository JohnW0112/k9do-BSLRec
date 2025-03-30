# -*- coding: utf-8 -*-
import socket
import threading
import time
from datetime import datetime
from naoqi import ALProxy

class MyClass(GeneratedClass):
    def __init__(self):
        print("[ReceiveGesture] Initializing box...")
        GeneratedClass.__init__(self)

        # === Setup Socket ===
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(("192.168.0.119", 5002))
            print("[ReceiveGesture] Socket bound to 192.168.0.119:5002")
        except Exception as e:
            print("[ReceiveGesture] Socket binding failed:", e)

        self.running = True
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()
        print("[ReceiveGesture] Socket listening thread started")

        # === Connect to Robot Proxies ===
        try:
            self.motion = ALProxy("ALMotion", "192.168.0.119", 9559)
            self.tts = ALProxy("ALTextToSpeech", "192.168.0.119", 9559)
            print("[ReceiveGesture] Proxies connected successfully")
            self.motion.wakeUp()
        except Exception as e:
            print("[ReceiveGesture] ERROR connecting proxies:", e)

    def listen(self):
        print("[ReceiveGesture] Listening for gesture commands...")
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                gesture = data.decode("utf-8").strip()
                print("[ReceiveGesture] Received:", gesture)
                self.perform_gesture(gesture)
            except Exception as e:
                print("[ReceiveGesture] Socket listen error:", e)

    def perform_gesture(self, gesture):
        print("[ReceiveGesture] perform_gesture() called with:", gesture)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if gesture == "wave":
                print("[Gesture] Executing WAVE")
                self.tts.say("Waving!")
                joint_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
                up_angles = [0.0, -0.5, 1.5, 1.0]
                down_angles = [1.5, 0.2, 1.2, 0.5]
                speed = 0.2
                self.motion.setAngles(joint_names, up_angles, speed)
                time.sleep(1.5)
                self.motion.setAngles(joint_names, down_angles, speed)
                print("[LOG]", [timestamp, gesture, "executed", "wave", "successful"])

            elif gesture == "point":
                print("[Gesture] Executing POINT")
                self.tts.say("Pointing!")
                self.motion.setAngles(["RShoulderPitch", "RShoulderRoll", "RElbowRoll"], [0.2, -0.3, 1.0], 0.2)
                print("[LOG]", [timestamp, gesture, "executed", "point", "successful"])

            elif gesture == "peace":
                print("[Gesture] Executing PEACE")
                self.tts.say("Peace!")
                self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.2)
                print("[LOG]", [timestamp, gesture, "executed", "peace", "successful"])

            else:
                print("[ReceiveGesture] Unknown gesture:", gesture)
                print("[LOG]", [timestamp, gesture, "skipped", "unknown gesture"])

        except Exception as e:
            print("[Gesture] Failed to execute:", e)
            print("[LOG]", [timestamp, gesture, "error", str(e)])

    def onUnload(self):
        print("[ReceiveGesture] onUnload() called — cleaning up")
        self.running = False
        try:
            self.sock.close()
            print("[ReceiveGesture] Socket closed")
        except:
            print("[ReceiveGesture] Failed to close socket")

    def onInput_onStart(self):
        print("[ReceiveGesture] onStart triggered")

    def onInput_onStop(self):
        print("[ReceiveGesture] onStop triggered")
        self.onUnload()
        self.onStopped()

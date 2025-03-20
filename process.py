#! /usr/bin/python3

import cv2
import numpy as np
import socket
import struct

# Connect to the Python 2 server
HOST = '127.0.0.1'  # Localhost
PORT = 56565  # Port to send commands
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

PORT_VIDEO = 5007  # Port for video stream
video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
video_socket.connect((HOST, PORT_VIDEO))

if __name__=="__main__":
    try:
        while True:
            # Receive frame size
            frame_size = struct.unpack("L", video_socket.recv(struct.calcsize("L")))[0]
            data = video_socket.recv(struct.calcsize("L"))
            if len(data) < 4:
                print("Warning: Received incomplete frame size. Skipping frame...")
                continue  # Skip this frame

            frame_size = struct.unpack("L", data)[0]


            # Receive frame data
            frame_data = b""
            while len(frame_data) < frame_size:
                frame_data += video_socket.recv(frame_size - len(frame_data))

            # Convert bytes to image
            frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((480, 640, 3))

            # Display video
            cv2.imshow("Pepper Camera Feed", frame)

            # Execute a series of action according to character
            '''
            Right now for testing purpose, I use keyboard inputs.
            '''
            while (key != 27):  # 27 is Esc
                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'):
                    client_socket.send(b'c')

                elif key == ord('l'):  # Raise Left Arm
                    client_socket.send(b'left')

                elif key == ord('r'):  # Raise Right Arm
                    client_socket.send(b'right')

                elif key == ord('b'):  # Raise Both Arms
                    client_socket.send(b'both')

                elif key == ord('p'):  # Point
                    client_socket.send(b'point')

                elif key == ord('w'):  # Wave
                    client_socket.send(b'wave')

                elif key == ord('f'):
                    client_socket.send(b'f')

    finally:
        client_socket.close()
        video_socket.close()
        cv2.destroyAllWindows()

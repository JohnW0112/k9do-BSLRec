#! /usr/bin/python3

import cv2
import numpy as np
import socket
import struct

# Connect to the Python 2 server
HOST = '127.0.0.1'  # Localhost
PORT = 5005  # Port to send commands
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

PORT_VIDEO = 5006  # Port for video stream
video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
video_socket.connect((HOST, PORT_VIDEO))

if __name__=="__main__":
    try:
        while True:
            # Receive frame size
            frame_size = struct.unpack("L", video_socket.recv(struct.calcsize("L")))[0]

            # Receive frame data
            frame_data = b""
            while len(frame_data) < frame_size:
                frame_data += video_socket.recv(frame_size - len(frame_data))
            print(len(frame_data))
            # Convert bytes to image
            frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((1280, 960, 3))
            
            # Display video
            cv2.imshow("Pepper Camera Feed", frame)

            # Execute a series of action according to character
            '''
            Right now for testing purpose, I use keyboard inputs.
            '''
            key = -1
            while (key != 27):          #27 is Esc
                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'):
                    client_socket.send(b'c')

                elif key == ord('z'):
                    client_socket.send(b'z')

                elif key == ord('f'):
                    client_socket.send(b'f')

    finally:
        client_socket.close()
        video_socket.close()
        cv2.destroyAllWindows()

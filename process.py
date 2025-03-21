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
video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
BUFFER_SIZE = 65535  # Max UDP packet size
video_socket.connect((HOST, PORT_VIDEO))

if __name__=="__main__":
    try:
        while True:
            # Receive image size first
            data, addr = video_socket.recvfrom(4)
            img_size = struct.unpack("!I", data)[0]

            # Receive image data
            img_data, _ = video_socket.recvfrom(img_size)

            # Convert the received data into an image
            np_arr = np.frombuffer(img_data, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is not None:
                cv2.imshow("Pepper Camera Feed", frame)

            # Execute a series of action according to character
            '''
            Right now for testing purpose, I use keyboard inputs.
            '''
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

            if key == ord('c'):
                client_socket.send(b'c')

            elif key == ord('z'):
                client_socket.send(b'z')

            elif key == ord('f'):
                client_socket.send(b'f')
        cv2.destroyAllWindows()
    finally:
        client_socket.close()
        video_socket.close()
        cv2.destroyAllWindows()

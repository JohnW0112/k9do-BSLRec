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


if __name__=="__main__":
    try:
        while True:


            # Execute a series of action according to character
            '''
            Right now for testing purpose, I use keyboard inputs.
            '''
            key = input("Enter command: ")
            print(key)
            

            if key == ord('c'):
                client_socket.send(b'c')

            elif key == ord('z'):
                client_socket.send(b'z')

            elif key == ord('f'):
                client_socket.send(b'f')

    finally:
        client_socket.close()
        cv2.destroyAllWindows()

#! /usr/bin/python3

import cv2
import socket

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
            

            if key == 'c':
                client_socket.send(b'c')

            elif key == 'z':
                client_socket.send(b'z')

            elif key == 'f':
                client_socket.send(b'f')

            elif key == '1':
                client_socket.send(b'1')

            elif key == '2':
                client_socket.send(b'2')
                
            elif key == '3':
                client_socket.send(b'3')

    finally:
        client_socket.close()


import socket
import time

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
WINDOW_SIZE = 100
RECEIVER_PORT = 5001 
SENDER_PORT = 6700

class UDPSender:
    def __init__(self, file_to_send):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind("0.0.0.0",SENDER_PORT)
        self.fileName = file_to_send
    
    def send():
        #open file
        #break file into packets of 1024 bytes each and store in a dict
        #send first 100 packets thru the network
        #acks 
        pass

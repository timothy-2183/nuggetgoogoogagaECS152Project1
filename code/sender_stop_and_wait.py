import socket
import time
# create socket outside because we can always reuse
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
receiverip = "127.0.0.1"
receiverport = "5001"

def main():
    with open('docker\file.mp3', 'read') as f:
        while True:
            chunk = f.read(1024) # we read 1024 bytes
            if not chunk:
                break
            # as of right noe we have the individual chunks of the data in 1024 bytes, now we can send
            # logic will be a modified version of this 
            # https://stackoverflow.com/questions/5343358/stop-and-wait-socket-programming-with-udp#:~:text=The%20stop%20and%20wait%20protocol,before%20sending%20the%20next%20packet.
            # the link is being done in C, but we're doing python now
            sock.sendto(chunk, ())

import socket
import time
import threading

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
EXTRA_BUFFER_SPACE = 5
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
WINDOW_SIZE = 100 * MESSAGE_SIZE
RECEIVER_IP_ADDRESS = '127.0.0.1'
RECEIVER_PORT = 5001 
SENDER_PORT = 0

class UDPSender:
    def __init__(self):
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.Socket.bind(("0.0.0.0",SENDER_PORT))
        self.DictOfPackets = {}
        self.SlidingWindow = []
        self.send100_done = False
    
    def send(self, file_to_send, receiver_ip_str, receiver_port):
        #set timeout and address tuple
        self.address = (receiver_ip_str, receiver_port)
        self.Socket.settimeout(1) #time out when NO packet is received
        #open file
        with open(file_to_send , 'rb') as f:
            file_data = f.read()
        #break file into packets of 1020 bytes each and store in a dict (add seq_id later to the packet's start)
        seq_id = 0
        for i in range(0, len(file_data), MESSAGE_SIZE):
            seq_id = i
            payload = file_data[seq_id:(seq_id + MESSAGE_SIZE)]
            seq_id_bytes = int.to_bytes(seq_id, SEQ_ID_SIZE, signed=True, byteorder='big')
            self.DictOfPackets[seq_id] = seq_id_bytes + payload

        #send first 100 packets thru the network
        self.send100()
      

        #manipulating the sliding window
        expected_ack_id = MESSAGE_SIZE
        while self.DictOfPackets:
            try:
                received_ack_packet, _ = self.Socket.recvfrom((SEQ_ID_SIZE + EXTRA_BUFFER_SPACE))
                received_ack_id = int.from_bytes(received_ack_packet[:SEQ_ID_SIZE],signed=True, byteorder='big')
                while (received_ack_id >= expected_ack_id):
                    packet_seq_id = expected_ack_id - MESSAGE_SIZE
                    if packet_seq_id in self.DictOfPackets:
                        self.DictOfPackets.pop(packet_seq_id)
                    if packet_seq_id in self.SlidingWindow:
                        self.SlidingWindow.remove(packet_seq_id)
                    expected_ack_id += MESSAGE_SIZE
                    if self.SlidingWindow:
                        next_seq_id = self.SlidingWindow[-1] + MESSAGE_SIZE
                        if next_seq_id in self.DictOfPackets:
                            packet = self.DictOfPackets[next_seq_id]
                            self.Socket.sendto(packet, self.address)
                            self.SlidingWindow.append(next_seq_id)
            except socket.timeout:
                print("TIMEOUT! RETRANSMITING")
                for seq_id in self.SlidingWindow:
                    packet = self.DictOfPackets[seq_id]
                    self.Socket.sendto(packet, self.address)
                    print(f"  Retransmitted packet {seq_id}")

        print("ALL PACKETS SENT") #DEBUG

        #finack
        seq_id = -1
        seq_id_bytes = int.to_bytes(seq_id, SEQ_ID_SIZE, signed=True, byteorder='big')
        fin_message = '==FINACK=='
        payload = fin_message.encode()
        packet = seq_id_bytes + payload
        self.Socket.sendto(packet, self.address)
        self.Socket.close()
    
    def send100(self):
        i = 0
        for seq_id in sorted(self.DictOfPackets):
            if (i == 100):
                break
            packet = self.DictOfPackets[seq_id]
            self.Socket.sendto(packet, self.address)
            self.SlidingWindow.append(seq_id)
            i += 1
        self.send100_done = True
        print(f"Initial window: {self.SlidingWindow[:10]}...")  # ← ADD THIS (first 10) DEBUG
    
    

def main():
    udp_sender = UDPSender()
    udp_sender.send('file.mp3', RECEIVER_IP_ADDRESS, RECEIVER_PORT)

if __name__ == "__main__": main()
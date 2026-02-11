import socket
import time

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
        self.ListOfAcks = []
    
    def send(self, file_to_send, receiver_ip_str, receiver_port):
        #set timeout and address tuple
        address = (receiver_ip_str, receiver_port)
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
        i = 0
        for seq_id in sorted(self.DictOfPackets):
            if (i == 100):
                break
            packet = self.DictOfPackets[seq_id]
            self.Socket.sendto(packet, address)
            self.SlidingWindow.append(seq_id)
            i += 1
        print(f"Initial window: {self.SlidingWindow[:10]}...")  # ← ADD THIS (first 10) DEBUG


        #receiving acks, and manipulating the slide window
        expected_ack_id = seq_id + MESSAGE_SIZE
        while self.DictOfPackets:
            print(f"Packets remaining: {len(self.DictOfPackets)}, Window: {len(self.SlidingWindow)}, Expected: {expected_ack_id}") # DEBUG
            try:
                print("Waiting for ACK...")  # ← Add this DEBUG
                received_ack_packet, _ = self.Socket.recvfrom((SEQ_ID_SIZE + EXTRA_BUFFER_SPACE))
                received_ack_id = int.from_bytes(received_ack_packet[:SEQ_ID_SIZE],signed=True, byteorder='big')
                print(f"Parsed ACK: {received_ack_id}")  # ← Add this DEBUG
                self.ListOfAcks.append(received_ack_id)
                while(expected_ack_id in self.ListOfAcks):
                    self.DictOfPackets.pop(expected_ack_id)
                    self.SlidingWindow.remove(expected_ack_id)
                    #expected_ack_id = self.SlidingWindow[0]
                    expected_ack_id += MESSAGE_SIZE
                    if self.SlidingWindow:
                        end_seq_id = self.SlidingWindow[-1]
                        new_end_seq_id = end_seq_id + MESSAGE_SIZE
                        if new_end_seq_id in self.DictOfPackets:
                            packet = self.DictOfPackets[new_end_seq_id]
                            self.Socket.sendto(packet, address)
                            self.SlidingWindow.append(new_end_seq_id)

            except socket.timeout:
                #re-send the packets in the SW:
                for seq_id in self.SlidingWindow:
                    packet = self.DictOfPackets[seq_id]
                    self.Socket.sendto(packet, address)
        
        #finack
        seq_id = -1
        seq_id_bytes = int.to_bytes(seq_id, SEQ_ID_SIZE, signed=True, byteorder='big')
        fin_message = '==FINACK=='
        payload = fin_message.encode()
        packet = seq_id_bytes + payload
        self.Socket.sendto(packet, address)
        self.Socket.close()



def main():
    udp_sender = UDPSender()
    udp_sender.send('file.mp3', RECEIVER_IP_ADDRESS, RECEIVER_PORT)

if __name__ == "__main__": main()
        

import socket
import time
import threading

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
EXTRA_BUFFER_SPACE = 5
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
WINDOW_PACKETS = 100
RECEIVER_IP_ADDRESS = '127.0.0.1'
RECEIVER_PORT = 5001 
SENDER_PORT = 0

class UDPSender:
    def __init__(self):
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.Socket.bind(("0.0.0.0",SENDER_PORT))
        self.Socket.settimeout(2)
        self.packetdict = {}
        self.packettp = {}
    
    def send(self, file_to_send, receiver_ip_str, receiver_port):
        #and address tuple
        address = (receiver_ip_str, receiver_port)
        #open file
        with open(file_to_send , 'rb') as f:
            file_data = f.read()
        #break file into packets of 1020 bytes each and store in a dict (add seq_id later to the packet's start)
        packets = {}
        for i in range(0, len(file_data), MESSAGE_SIZE):
            payload = file_data[i:i + MESSAGE_SIZE]
            seq_id_bytes = i.to_bytes(SEQ_ID_SIZE, signed=True, byteorder='big')
            packets[i] = seq_id_bytes+payload

        base = 0
        nxt_sq = 0
        win_sz = WINDOW_PACKETS*MESSAGE_SIZE
        file_size = len(file_data)

        #start transmitting the message from here
        while base < file_size:
            while nxt_sq < base + win_sz and nxt_sq < file_size:
                self.packetdict[nxt_sq] = time.time()
                self.Socket.sendto(packets[nxt_sq],address)
                nxt_sq+= MESSAGE_SIZE

            try:
                ack_packet, _ = self.Socket.recvfrom(PACKET_SIZE)
                ack = int.from_bytes(ack_packet[:SEQ_ID_SIZE], byteorder= 'big', signed = True)
                #this part to measure individual packet throughput
                seq = base 
                while seq < ack:
                    if seq in self.packetdict:
                        t_send = self.packetdict[seq]
                        t_ack = time.time()
                        packettp = MESSAGE_SIZE / (t_ack-t_send)
                    seq+=MESSAGE_SIZE
                #move the sliding window
                if ack> base:                         
                    base = ack
            except socket.timeout:
                resend = base
                while resend < nxt_sq:
                    self.Socket.sendto(packets[resend], address)
                    self.packetdict[resend] = time.time()
                    resend += MESSAGE_SIZE

        #finack
        fin_seq = (-1).to_bytes(SEQ_ID_SIZE, byteorder='big', signed=True)
        self.Socket.sendto(fin_seq + b'==FINACK==', address)
        self.Socket.close()
    

def main():
    udp_sender = UDPSender()
    start = time.time()
    udp_sender.send('file.mp3', RECEIVER_IP_ADDRESS, RECEIVER_PORT)
    end = time.time()
    print(end-start)
    avg = sum(udp_sender.packetdict.values())/len(udp_sender.packetdict)
    print(f"{avg:.7f}")
    print(f"{0.3*(end-start)/1000 + 0.7/avg:.7f}")

if __name__ == "__main__": main()
import socket
import time
# create socket outside because we can always reuse, also set timeout.

receiverip = "127.0.0.1"
receiverport = 5001
packet_sz = 1024                    
sequence_id_size = 4
data_sz = packet_sz-sequence_id_size
tp = []
ppd = []

def send():
    starttp = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    # we always start from packet 0
    seqnum = 0
    with open('file.mp3', 'rb') as f:
        while True:
            chunk = f.read(packet_sz-sequence_id_size) 
            if not chunk:
                break
            # as of right now we have the individual chunks of the data in 1024 bytes, now we can send
            packet = seqnum.to_bytes(sequence_id_size, 'big') + chunk
            ackget =  False
            startppd = time.time()
            while not ackget:
                #send here regardless of outcome
                sock.sendto(packet,(receiverip, receiverport))
                try:
                    #wait until u receive something
                    ackpacket, _ = sock.recvfrom(packet_sz)
                    acknum = int.from_bytes(ackpacket[:sequence_id_size], 'big')
                    #if correct, u just add smth more if not then just do nothing because the while will just retransmit
                    if acknum > seqnum:
                        ackget = True
                        # we don't add it by a full 1028 because there may be a chance that it reaches an end and does not read a full 1024 byte and then it causes issues
                        seqnum = acknum
                        endppd = time.time()
                        ppd.append(endppd-startppd)
                    
                except (socket.timeout,ConnectionResetError):
                    pass
    eof_packet = seqnum.to_bytes(sequence_id_size, 'big')
    fin_received = False
    while not fin_received:
        sock.sendto(eof_packet,(receiverip, receiverport))    
        try:
            packet, _ = sock.recvfrom(packet_sz)
            msg = packet[sequence_id_size:]
            if msg == b'fin': 
                fin_received = True
        except socket.timeout:
            pass
    finack = seqnum.to_bytes(sequence_id_size, 'big') + b'==FINACK=='
    sock.sendto(finack, (receiverip, receiverport))
    sock.close()
    endtp= time.time()
    tp.append(endtp-starttp)
def main():
    send()
    avgtp = sum(tp)/len(tp)
    avgppd = sum(ppd)/len(ppd)
    print("Throughput: ", f"{avgtp:.7f}")
    print("Per-packet delay: ", f"{avgppd:.7f}")
    print("Performance:", f"{0.3*avgtp/1000 + 0.7/avgppd:.7f}")

if __name__ == "__main__": main()
import socket

receiver_ip = "127.0.0.1"
receiver_port = 5001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data = b"Hello, receiver!"
seqnum = 0
for _ in range(100): 
    packet = seqnum.to_bytes(4, 'big') + data
    sock.sendto(packet, (receiver_ip, receiver_port))
    print("Packet sent!")
    try:
        ack_packet, _ = sock.recvfrom(1024)
        ack_num = int.from_bytes(ack_packet[:4], 'big')
        print("Received ACK number:", ack_num)
        if ack_num >= seqnum:
            seqnum = ack_num
    except socket.timeout:
        print("No ACK received, timed out")

sock.close()
#this works, time to wait until the ack is properly obtained.
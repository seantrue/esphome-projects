import time
import socket
UDP_IP_ADDRESS = "192.168.2.130"
UDP_PORT_NO = 21324

def sendColor(color):
    v = [2, 10 ] + color*24
    Message = bytearray(v)
    clientSock = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.sendto (Message, (UDP_IP_ADDRESS, UDP_PORT_NO))

for i in range(256):
    sendColor([i,i,i])
    time.sleep(.1)
    

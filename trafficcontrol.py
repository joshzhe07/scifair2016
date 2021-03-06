import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
carhost,carport,message=sys.argv[1],int(sys.argv[2]),sys.argv[3]
server_address = (carhost, carport)

try:

    # Send data
    print >>sys.stderr, 'sending "%s"' % message
    sent = sock.sendto(message, server_address)

    # Receive response
    # print >>sys.stderr, 'waiting to receive'
    # data, server = sock.recvfrom(4096)
    # print >>sys.stderr, 'received "%s"' % data

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()

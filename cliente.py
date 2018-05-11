#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The client program sets up its socket differently from the way a server does. Instead of binding to a port and listening, it uses connect() to attach the socket directly to the remote address.

import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

# After the connection is established, data can be sent through the socket with sendall() and received with recv(), just as in the server.

messages = ['0.0 CREATE CPUTIME 5',
            '0.0 CREATE CPUTIME 3',
            '0.7 CREATE CPUTIME 1',
            '1.0 QUANTUM',
            '2.0 QUANTUM',
            '2.5 CREATE CPUTIME 2',
            '3.0 QUANTUM',
            '3.0 KILL 3',
            '3.0 CREATE CPUTIME 4',
            '3.0 CREATE CPUTIME 3',
            '4.0 QUANTUM',
            '5.0 QUANTUM',
            '5.3 CREATE CPUTIME 1',
            '6.0 QUANTUM',
            '7.0 QUANTUM',
            '8.0 QUANTUM',
            '9.0 QUANTUM',
            '10.0 QUANTUM',
            '10.6 KILL 2',
            '11.0 QUANTUM',
            '11.0 KILL 7',
            '12.0 QUANTUM',
            '12.0 KILL 4',
            '13.0 QUANTUM',
            '14.0 QUANTUM',
            '15.0 QUANTUM',
            '16.0 QUANTUM',
            '16.7 INICIA I/O 5',
            '16.7 KILL 6',
            '17.5 TERMINA I/O 5',
            '17.5 QUANTUM',
            '17.5 KILL 1',
            '18.0 QUANTUM',
            '18.0 KILL 5',
            '19.0 QUANTUM',
            '19.4 END']

try:
    
    # Send data
    for m in messages:
        print >>sys.stderr, 'client sending "%s"' % m
        sock.sendall(m)

        # Look for the response
    
        respuesta = sock.recv(256)
        
        print >>sys.stderr, 'client received "%s"' % respuesta

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()

  


def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))


#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import time
import new_base


seguimiento = False
algorithm = sys.argv[1]
cpus_quantity = 1
quantum = 1
cc = 0

if algorithm == 'SJF' or algorithm == 'SRT':
    scheduler = new_base.CPUScheduler(cpus_quantity, quantum, cc)
    seguimiento = True
else:
    print >>sys.stderr, 'Algoritmo desconocido'


if seguimiento:

    # configuracion del servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    # print >> sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    sock.listen(1)

    print >>sys.stderr, 'Esperando por un cliente'
    connection, client_address = sock.accept()

    try:
        # se ha podido realizar la coneccion
        print >>sys.stderr, 'Se establecio coneccion con', client_address

        while True:   
            # recibe los datos
            data = connection.recv(256)

            # si recibe informacion
            if data:
                # llama a la funcion para ejecutar el comando
                client_message = scheduler.execute_command(new_base.Command(data), algorithm)

                connection.sendall(client_message)
            else:
                connection.close()
                sys.exit()
                
    finally:
        scheduler.imprimir_resumen()
        scheduler.impresion_final()
        print >>sys.stderr, 'Termina servidor'
        connection.close()



def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

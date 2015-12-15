#!/usr/bin/env python

"""
A chat server that can handle up to 5 concurrent clients at a time.
Entering 'stop' at the terminal will exit the server.
"""

import select
import socket
import sys


class Server:
    def __init__(self):
        self.host = ''
        self.port = 5000
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.socket_connections = []

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(self.backlog)
            print 'Chat server started on port {port}'.format(port=self.port)
        except socket.error, (error_code, message):
            if self.server:
                self.server.close()
            print 'Could not open socket. Error code: {error_code} Message: {message}.'.format(error_code=error_code, message=message)
            sys.exit(1)

    def run(self):
        self.open_socket()
        self.socket_connections = [self.server, sys.stdin]
        running = True
        while running:
            ready_to_read, ready_to_write, ready_to_except = select.select(self.socket_connections, [], [])

            for s in ready_to_read:
                # handle new client connections to the server
                if s == self.server:
                    socket_obj, address = self.server.accept()
                    self.socket_connections.append(socket_obj)
                    print 'Client at {host}: {port} has connected.'.format(host=address[0], port=address[1])
                    self.broadcast(socket_obj, '\r{address} entered the chat room.\n'.format(address=address))
                # handle standard input
                elif s == sys.stdin:
                    cmd = sys.stdin.readline()
                    print 'Server received: {cmd}'.format(cmd=cmd)
                    print 'Stopping the server...'
                    running = False
                # handle messages received from clients
                else:
                    try:
                        data = s.recv(self.size)
                        if data.startswith('/quit'):
                            print 'Client {client_name} has disconnected.'.format(client_name=str(s.getpeername()))
                            self.broadcast(self.server, '\rClient {client_name} is offline'.format(client_name=str(s.getpeername())))
                            s.close()
                            self.socket_connections.remove(s)
                        elif data:
                            self.broadcast(s, '\r[{client_name}]: {message}'.format(client_name=str(s.getpeername()), message=data))
                    # Unless the client disconnected by itself
                    except socket.error, (error_code, message):
                        print 'Could not read from socket. Error code: {error_code} Message: {message}.'.format(error_code=error_code, message=message)
                        s.close()
                        self.socket_connections.remove(s)
        self.server.close()

    def broadcast(self, origin_socket, message):
        for s in self.socket_connections:
            # send the message only to other clients
            if s is not self.server and s is not sys.stdin and s is not origin_socket:
                try:
                    s.send(message)
                except Exception:
                    s.close()
                    self.socket_connections.remove(s)


if __name__ == '__main__':
    s = Server()
    s.run()

#!/usr/bin/env python

"""
An echo client that allows the user to send multiple lines to the server.
Entering a blank line will exit the client.
"""
import select
import socket
import sys


class Client(object):
    def __init__(self):
        self.host = ''
        self.port = 5000
        self.size = 1024
        self.server_socket = None
        self.socket_connections = []

    def connect_to_host(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.host, self.port))
            print 'Connected to chat server. You can start sending messages.'
            self.prompt()
        except socket.error, (code, message):
            print "There was an error connecting. Error code: {code} Message: {message}".format(code=code, message=message)
            sys.exit(1)

    def prompt(self):
        sys.stdout.write('[Me]: ')
        sys.stdout.flush()

    def run(self):
        self.connect_to_host()
        self.socket_connections = [self.server_socket, sys.stdin]
        running = True
        while running:
            read_sockets, write_sockets, error_sockets = select.select(self.socket_connections, [], [])

            for s in read_sockets:
                # handle incoming message from chat server
                if s == self.server_socket:
                    data = s.recv(self.size)
                    if not data:
                        print '\rDisconnected from chat server.'
                        s.close()
                        sys.exit(1)
                    else:
                        sys.stdout.write(data)
                        self.prompt()
                # send client messages to the chat server
                else:
                    data = sys.stdin.readline()
                    self.server_socket.send(data)
                    self.prompt()


if __name__ == "__main__":
    c = Client()
    c.run()

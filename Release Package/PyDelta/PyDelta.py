"""
Author: THD
Date: April 7, 2016
version: 1.0
"""

import socket
import threading
import sys

logged_in_user = ''
exit_client = False

class IncomingThread(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock  # Initialize data for thread

    def run(self):
        try:
            while True:
                global exit_client
                if exit_client:
                    return
                # TODO: should use select() and recv() instead of recvform()
                data, address = self.sock.recvfrom(1024)
                if data[-16:] == "LOGIN SUCCESSFUL":
                    elements = data.split()
                    global logged_in_user
                    logged_in_user = elements[0]
                print str(data)
        except socket.error:
            pass

# Trick: Make config file in python
# Ref: http://stackoverflow.com/questions/8225954/python-configuration-file-any-file-format-recommendation-ini-format-still-appr
config = {}
execfile("Server.conf", config)
SERVER_ADDR = config["server"]
PORT = 49512

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_ADDR, PORT))
print ">> Connected to Server"
thread_incoming = IncomingThread(client_socket)
thread_incoming.start()

inp = ''
while inp != 'exit':
    inp = raw_input()
    if inp != '':
        parts = inp.split()
        # split(arg) here can  cause error, for example: split(2) error with inp = "LOGIN dangdangkhtn"
        prefix = parts[0]
        if prefix == 'MSG':
            if logged_in_user != '':
                temp = inp.split(' ', 2)
                des = temp[1]
                content = temp[2]
                inp = 'MSG ' + logged_in_user + ' ' + des + ' ' + content
            else:
                print 'please login before send message!'
                continue
        client_socket.send(inp)

client_socket.close()


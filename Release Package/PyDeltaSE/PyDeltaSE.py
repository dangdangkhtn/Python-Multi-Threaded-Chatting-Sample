"""
Author : dangdangkhtn
Date: April 7, 2016
version: 1.0

Ref: PythonNetBinder.pdf at entry Asynchronous Server (Page 1-52)
Ref: Python Standard Library: at entry Network Protocols / The select module  (Page 7-10)
Ref: https://pymotw.com/2/select/
"""

import time
import socket
import select
import Queue
import Authenticate


IP = '0.0.0.0'  # To make server listening on all NIC card.
PORT = 49512

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen(5)
print ">> Server Started"
auth_module = Authenticate.Authenticate()  # Authenticate module
clients = []         # List of client sockets object connecting
message_queues = {}  # Pair : <client socket> : <queue>
users = {}           # Pair : <string username> : <client socket>
watches_incoming = [server_socket]  # List of sockets need to be watches to detect incoming signal by 'select' module

while True:
    # Monitor all sockets and detect activity on that sockets
    readable_socks, writable_socks, err = select.select(watches_incoming, clients, [])
    for sock in readable_socks:
        if sock is server_socket:
            # A "readable" server socket is ready to accept a connection
            socket_conn, tuple_client_addr = server_socket.accept()
            print '(%s, %s) connected' % tuple_client_addr
            socket_conn.setblocking(0)
            watches_incoming.append(socket_conn)
            # Add this socket to clients list to watches for outgoing signal by 'select' module
            clients.append(socket_conn)
            # Give the connection a queue for data we want to send
            message_queues[socket_conn] = Queue.Queue()

        else:  # A message come from a client, that message is waiting to be get.
            data = ''
            try:
                data = sock.recv(1024)
            except:   # client crashed, do nothing here and let code below close the connection.
                pass  # This try-except block just for avoid server crash by exception when a client crashed
            if data:
                # A readable client socket has data
                print 'received "%s" from %s' % (data, sock.getpeername())
                elements = data.split(" ", 3)
                prefix = elements[0]

                if prefix == "LOGIN" and len(elements) == 3:  # message template "LOGIN <username> <password>"
                    usr_name = elements[1]
                    pwd = elements[2]
                    # Authenticate and response to client
                    if auth_module.authenticate(usr_name, pwd):
                        message_queues[sock].put(usr_name + " LOGIN SUCCESSFUL")
                        users.update({usr_name: sock})  # Add new user to list of user which is connecting
                        print "\t" + usr_name + " logged in"
                    else:
                        message_queues[sock].put("LOGIN FAILED")

                elif prefix == "REGISTER" and len(elements) == 3:
                    usr_name = elements[1]
                    pwd = elements[2]
                    # Check if account exist in DB
                    if auth_module.account_registered(usr_name):
                        message_queues[sock].put(usr_name + " ACCOUNT IS REGISTERED")
                    else:
                        auth_module.register(usr_name, pwd)
                        message_queues[sock].put("CREATE ACCOUNT " + usr_name + " SUCCESSFUL")

                elif prefix == "MSG" and len(elements) == 4:  # message template "MGS <src> <des> <content>"
                    src_name = elements[1]
                    des_name = elements[2]
                    content = elements[3]
                    # if des_name is logged in
                    if des_name in users:
                        des_socket = users[des_name]
                        message_queues[des_socket].put(src_name + " say: " + content)
                    else:
                        message_queues[sock].put(des_name + " IS NOT ONLINE")

                elif prefix == "GETLIST" and len(elements) == 1:  # message template "GETLIST"
                    user_names = users.keys()
                    if len(user_names) == 0:
                        message_queues[sock].put("NO USER ONLINE")
                    for usr_name in user_names:
                        message_queues[sock].put(usr_name)
                else:
                    message_queues[sock].put("SERVER RESPONSE: INVALID COMMAND")

            else:  # Client disconnected
                peer_name = sock.getpeername()
                print 'close (%s, %s)' % peer_name
                clients.remove(sock)
                watches_incoming.remove(sock)
                # Technical ref: Remove an item by value
                # http://stackoverflow.com/questions/5447494/best-way-to-remove-an-item-from-a-python-dictionary
                users = {key: value for key, value in users.items() if value != sock}
                # To stop examine this sock in writable_socks loop (strong logic)
                writable_socks.remove(sock)
                sock.close()
                # Remove message queue
                del message_queues[sock]
                print '(%s, %s) closed' % peer_name

    for sock in writable_socks:
        try:
            msg = message_queues[sock].get_nowait()
        except Queue.Empty:
            pass
        else:
            sock.send(msg)
            time.sleep(0.01)  # sleep 10ms

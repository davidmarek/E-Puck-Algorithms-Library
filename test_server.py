#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import readline

if __name__ == '__main__':
    s = socket.socket()
    s.bind(('127.0.0.1', 65432))
    s.listen(1)
    client, _ = s.accept()
    print "Connected client: %s" % client
    try:
        while True:
            msg = client.recv(255)
            print msg
            command = raw_input()
            client.send(command)
    except KeyboardInterrupt:
        client.close()
        s.close()

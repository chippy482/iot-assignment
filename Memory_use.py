#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 17:16:19 2020

@author: chippy
"""

import socket
import psutil
import time

# function for sneding memory usage usage message to server
def socket_connection():
    ip_port = ("127.0.0.1",8080)
    #using port 8080 for connection
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ip_port) 
    client.settimeout(60)
    while True:    
        try:
            memory = {'Key':'Virtual_Memory','Value': psutil.virtual_memory()[2]}
            print(memory)
            client.send(str(memory).encode())
            time.sleep(45)
        except socket.error as error:
            print(error)
            client.close()    
        
if __name__ == '__main__' :
    socket_connection()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 17:16:19 2020

@author: chippy
"""

import socket 
import sqlite3
import datetime
from threading import Thread 

connection = sqlite3.connect("Mytab.db", check_same_thread=False)
server_conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

ip_port = ("127.0.0.1",8080)
connection = connection.cursor()

thread_list=list()


class client(Thread): 
 
    def __init__(self,ip,port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
 
    def run(self): 
       server_conn.listen(4) 
       (conn,(ip,port)) = server_conn.accept() 
       while True : 
            data = conn.recv(2048)
            msg = data.decode()
            message = eval(msg) 
            dataStore(message,ip,port)
            if not data: 
                break
            conn.send(data) 
 

def create_table():
#CREATING NEW TABLE USING SQLITE
    
    connection.execute("CREATE TABLE IF NOT EXISTS CpuInfo (DateTime TEXT, Key TEXT, Value REAL)")

def dataStore(message,ip,port):
    print(message)
    key_value = message['Key']
    val = message['Value']
    if(key_value == 'CPU_Usage' ):
            if(float(val > 30.0)):
                val_list = list()
                val_list.append(str(datetime.datetime.now()))
                val_list.append("CPU_Usage")
                val_list.append(val)
                print("CPU Usage is more than 30%")
                try:
                    connection.execute("Insert into CpuInfo (DateTime, Key, Value ) VALUES (?,?,?)",tuple(val_list))
                    val_list.clear()
                    print(" CPU Usage greater than 30% is inserted")
                except sqlite3.Error as error:
                    print(error)
    elif(key_value == 'Virtual_Memory'):
        if(float(val>40.0)):
            val_list = list()
            val_list.append(str(datetime.datetime.now()))
            val_list.append("Virtual_Memory")
            val_list.append(val)
            print("Memory Usage is more than 40%")
            try:
                connection.execute("Insert into CpuInfo (DateTime, Key, Value ) VALUES (?,?,?)",tuple(val_list))
                val_list.clear()
                print(" Memory Usage greater than 40% is inserted")
            except sqlite3.Error as error:
                print(error)
            
def main_function():
 
    create_table()
    server_conn.bind(ip_port)
    server_conn.listen(5) 
    (conn, (ip,port)) = server_conn.accept() 

    while True: 
        message_recv = conn.recv(1024)
        dt = eval(message_recv)
        dataStore(dt,ip,port)
        newthread = client(ip,port)
        newthread.start() 
        thread_list.append(newthread) 
     
    for i in thread_list: 
        i.join()      

if __name__ =="__main__":
         main_function()
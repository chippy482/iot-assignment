

import socket
import psutil
import time


    
        
        
        
if __name__ == '__main__' :
    socket_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    ip_port = ("127.0.0.1",8080)
    socket_client.connect(ip_port) 
    socket_client.settimeout(60)
    while 1:    
        try:
            dataFrame = {'Key':'CPU','Value': psutil.cpu_percent()}
            print(dataFrame)
           
            socket_client.send(str(dataFrame).encode())
            
            time.sleep(3)
        except Exception as ex:
            print(ex)
            socket_client.close()
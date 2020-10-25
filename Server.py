

import socket 
from threading import Thread 
import sqlite3
import paho.mqtt.client as mqtt

thread_process_list=list()
connection = sqlite3.connect("MyDb.db", check_same_thread=False)
tlreadList = [] 
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

c= connection.cursor()


#Multithread
class ClientThread(Thread): 
 
    def __init__(self,ip,port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
 
    def run(self): 
       server.listen(4) 
       (conn, (ip,port)) = server.accept() 
       
       while True : 
            data = conn.recv(2048)
            msg = data.decode()
            dt = eval(msg) 
            print(dt)
            dataProcess(dt,ip,port)


            if not data: 
                break
            conn.send(data) 
 
class PubSubThread(Thread):
    def __init__(self,topic):
        Thread.__init__(self)
        self.topic = topic
    def run(self):
        client = mqtt.Client('Chippy')
        client.on_message = on_message  
        client.connect("broker.hivemq.com")
        client.subscribe('topic/mem_request')
        client.subscribe("topic/cpu_request")
        
        client.loop_forever() 
        
def on_message(client,userdata,message):
     
    
    
        
    if(str(message.topic)=="topic/mem_request" ):
        print("topic/mem_request")
   
        try:
            query = "Select * from MyDb Where Key = 'MEM' Order by id DESC LIMIT 10"
            print(query)
            
            datas = c.execute(query)
        except sqlite3.Error as error:
            print(error)
        myList = []
        for d in datas:
            myList.append(d[2])
        print(str(myList))
        
        
        client.publish("topic/mem_reply",str(myList))
        
    elif(str(message.topic)=="topic/cpu_request" ):
        print("topic/cpu_request")
        try:
            query = "Select * from MyDb Where Key = 'CPU' Order by id DESC LIMIT 10"
            print(query)
            
            datas = c.execute(query)
        except sqlite3.Error as error:
            print(error)
        myList = []
        for d in datas:
            print(d)
            myList.append(d[2])
        print(str(myList))
        
        
        
        client.publish("topic/cpu_reply",str(myList))
    

  
  

    
    
   
    
   

    
    
def dataProcess(dt,ip,port):
    if(dt['Key']=='CPU'):
            if(float(dt['Value']>30.0)):
                valueList = list()
                valueList.append(dt['Key'])
                valueList.append(dt['Value'])
                print("CPU Usage more than 30%")
                try:
                    c.execute("Insert into MyDb ( Key, Value ) VALUES (?,?)",tuple(valueList))
                    valueList.clear()
                    connection.commit()
                    print("Inserted CPU Usage")
                except sqlite3.Error as error:
                    print(error)
    elif(dt['Key']=='MEM'):
        if(float(dt['Value']>40.0)):
            valueList = list()
            valueList.append(dt['Key'])
            valueList.append(dt['Value'])
            print("Memory Usage more than 40%")
            try:
                c.execute("Insert into MyDb ( Key, Value ) VALUES (?,?)",tuple(valueList))
                valueList.clear()
                connection.commit()
                print("Inserted Memory Usage")
            except sqlite3.Error as error:
                print(error)

   

if __name__ =="__main__":
    c.execute("CREATE TABLE IF NOT EXISTS MyDb (id INTEGER PRIMARY KEY AUTOINCREMENT,Key TEXT ,Value REAL)")
    server.bind( ("127.0.0.1",8080))
    server.listen(4) 
    (conn, (ip,port)) = server.accept() 
    tlreadList.append(PubSubThread("topic/cpu_request").start())
    while 1: 
        message_recv = conn.recv(1024)
        dt = eval(message_recv)
        dataProcess(dt,ip,port)

        newthread = ClientThread(ip,port)
        newthread.start() 
        tlreadList.append(newthread) 
     
    for t in tlreadList: 
        t.join()
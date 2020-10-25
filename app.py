
import eventlet
import json
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message



eventlet.monkey_patch()


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_CLEAN_SESSION'] = True
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
app.config['MQTT_LAST_WILL_MESSAGE'] = 'bye'
app.config['MQTT_LAST_WILL_QOS'] = 2



app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "chipiot8@gmail.com"
app.config['MAIL_PASSWORD'] = "iot@2020"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config.from_object(__name__)

mqtt = Mqtt(app)
mail =  Mail(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)


cpu = False
mem = False


@app.route('/')
def index():
    return render_template('index.html')




@socketio.on('publish')
def handle_publish(json_str):
    global cpu
    global mem
    print("Publish is "+json.loads(json_str)['topic'])
    if(json.loads(json_str)['topic']=="topic/cpu_request"):
        mqtt.publish(json.loads(json_str)['topic'],'nothing')
        cpu = True
        mem = False
        mqtt.subscribe('topic/cpu_reply')
    if(json.loads(json_str)['topic']=="topic/mem_request"):
        mqtt.publish(json.loads(json_str)['topic'],'nothing')        
        mqtt.subscribe('topic/mem_reply')
        cpu = False
        mem = True
    




@socketio.on('subscribe')
def handle_subscribe(json_str):
   
    print(json.loads(json_str))
   
    if(json.loads(json_str)['topic'=='topic/cpu_reply']):
         mqtt.subscribe(json.loads(json_str)['topic'])
         
         print('Subscribing in '+json.loads(json_str)['topic'])
    elif(json.loads(json_str)['topic'=='topic/mem_reply']):
         mqtt.subscribe(json.loads(json_str)['topic'])
         print('Subscribing in '+json.loads(json_str)['topic'])
         


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode(),
        qos=message.qos,
    )
    socketio.emit('mqtt_message', data=data)
    items = data['payload']
    if(cpu):
        items = items[1:-1]
        items = items.split(',')
        print(items)
        for item in items:
            print(item)
            if(float(item)>50.00):
                sendEmail = True
                
    
            
    elif(mem):
        items = items[1:-1]
        items = items.split(',')
        print(items)
        for item in items:
            print(item)
            if(float(item)>80.00):
                sendEmail = True
                
    if(sendEmail):
        
        msg =""
        if(cpu):
            message="CPU usage of IoT device is more than 50 percentage"
        elif(mem):
            message = "Memory usage of IoT device is more than 80 percentage"
        try:
            with app.app_context():
                msg = Message("IoT MQTT",
                    sender="iotmqttipr@gmail.com",
                    recipients=['chippymathew4@gmail.com'])
                msg.body= message
                print(msg)
                mail.send(msg)
        except Exception as ex:
            print(str(ex))
            



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
    



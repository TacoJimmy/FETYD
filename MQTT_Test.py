import codecs
# -*- coding: UTF-8 -*-
import paho.mqtt.client as mqtt
import json
import time  

client = mqtt.Client()
client.username_pw_set("acme","85024828")
client.connect("210.68.227.123", 3881, 60)

def IPC_Func():
    payload_ipc = {"Bank_Name":"南京分公司",
                   "Bank_longitude":25.052522264728704,
                   "Bank_latitude":121.53113679494496,
                   "Bank_administrator":"張三",
                   "Device_manufacturer":"遠傳電信"
                   }
    print (json.dumps(payload_ipc))
    client.publish("yuanta/ipc", json.dumps(payload_ipc))
    
def Elec_Func():
    payload_elec = {"mainpowertype":"三相四線",
                   "voltage":220,
                   "current_r":10
                   }
    print (json.dumps(payload_elec))
    client.publish("yuanta/electricity", json.dumps(payload_elec))
    
def Water_Func():
    payload_WaterNode = {"WaterNode_01":1}
    print (json.dumps(payload_WaterNode))
    client.publish("yuanta/water", json.dumps(payload_WaterNode))
    
def Fire_Func():
    payload_fire = {"FireNode_01":1}
    print (json.dumps(payload_fire))
    client.publish("yuanta/fire", json.dumps(payload_fire))
    
def TempHumi():
    payload_TempHumi = {"Temperature":40,"Humidity":70}
    print (json.dumps(payload_TempHumi))
    client.publish("yuanta/th", json.dumps(payload_TempHumi))
    
def earthquake():
    payload_earthquake = {"earthquake":0,"sensor_alive":1}
    print (json.dumps(payload_earthquake))
    client.publish("yuanta/earthquake", json.dumps(payload_earthquake))
    
def earthquake_alarm():
    payload_earthquakealarm = {"earthquake_alarm":1}
    print (json.dumps(payload_earthquakealarm))
    client.publish("yuanta/earthquake_error", json.dumps(payload_earthquakealarm))
    
def Temperature_alarm():
    payload_temperaturealarm = {"Temperature":0}
    print (json.dumps(payload_temperaturealarm))
    client.publish("yuanta/th_error", json.dumps(payload_temperaturealarm))

def Humidity_alarm():
    payload_Humidityalarm = {"Humidity":0}
    print (json.dumps(payload_Humidityalarm))
    client.publish("yuanta/th_error", json.dumps(payload_Humidityalarm))

def fire_alarm():
    payload_firealarm = {"FireNode_error_01":0}
    print (json.dumps(payload_firealarm))
    client.publish("yuanta/fire_error", json.dumps(payload_firealarm))
    

def water_alarm():
    payload_wateralarm = {"WaterNode_error_01":0}
    print (json.dumps(payload_wateralarm))
    client.publish("yuanta/water_error", json.dumps(payload_wateralarm))

def elec_alarm():
    payload_elecalarm = {"voltage_error_r":0}
    print (json.dumps(payload_elecalarm))
    client.publish("yuanta/electricity_error", json.dumps(payload_elecalarm))

if __name__ == '__main__':
    while True:
        IPC_Func()
        Elec_Func()
        Water_Func()
        Fire_Func()
        TempHumi()
        earthquake()
        elec_alarm()
        
        time.sleep(10)
        
        
        
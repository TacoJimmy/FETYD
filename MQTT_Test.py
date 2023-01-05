import codecs
# -*- coding: UTF-8 -*-
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import paho.mqtt.client as mqtt
import json
import time
import schedule  




glo_fire_flag = 0
glo_people_flag = 0
glo_temp_flag = 0
client = mqtt.Client()
client.username_pw_set("acme","85024828")
client.connect("210.68.227.123", 3881, 60)


master = modbus_rtu.RtuMaster(serial.Serial(port='/dev/ttyS1', baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
master.set_timeout(5.0)
master.set_verbose(True)


ser = serial.Serial(port='/dev/ttyS4', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)



def setmqtt():
    glo_fire_flag = 0
    glo_people_flag = 0
    glo_temp_flag = 0
    client = mqtt.Client()
    client.username_pw_set("acme","85024828")
    client.connect("210.68.227.123", 3881, 60)

def setmodbus():
    master = modbus_rtu.RtuMaster(serial.Serial(port='/dev/ttyS1', baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
    master.set_timeout(5.0)
    master.set_verbose(True)

def setascii():
    ser = serial.Serial(port='/dev/ttyS4', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)



def get_FirePeople():
    ser.write(b'$016\r\n') # send command for gate Di data
    output = ser.read(9) # Read 9 bytes from serial buffer 
    #print (output)
    output2 = str(output)
    FirePeople_status = int(output2[4])
    
    
    if FirePeople_status == 2 or FirePeople_status == 3:
        Fire_status = 1
    else:
        Fire_status = 0
        
    if FirePeople_status == 1 or FirePeople_status == 3:
        People_status = 1
    else:
        People_status = 0
    
    return Fire_status,People_status

def get_ADAM():
    ser.write(b'$016\r\n') # send command for gate Di data
    output = ser.read(9) # Read 9 bytes from serial buffer 
    
    return output

def get_temphumi():
    temp = master.execute(10, cst.READ_HOLDING_REGISTERS, 3, 2) 
    time.sleep(0.5)
    evm_temp = round(temp[0]*0.01,1)
    evm_humi = round(temp[1]*0.01,1)
    
    return evm_temp,evm_humi

def get_earthquake():
    earth = master.execute(1, cst.READ_HOLDING_REGISTERS, 286, 2) 
    time.sleep(0.5)
    earth_level = round(earth[0])
    earth_value = round(earth[1])
    
    return earth_level,earth_value

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
    
def Fire_Func(fire_status):
    payload_fire = {"FireNode_01":fire_status}
    print (json.dumps(payload_fire))
    client.publish("yuanta/fire", json.dumps(payload_fire))
    
def peopledetec_Func(people_status):
    payload_peopledetec = {"PeopleDetec":people_status}
    print (json.dumps(payload_peopledetec))
    client.publish("yuanta/peopledetec", json.dumps(payload_peopledetec))
    
def TempHumi(temp,humi):
    payload_TempHumi = {"Temperature":temp,"Humidity":humi}
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

def peopledetec_alarm():
    peopledetec_alarm = {"PeopleDetec_alarm":0}
    print (json.dumps(peopledetec_alarm))
    client.publish("yuanta/peopledetec_error", json.dumps(peopledetec_alarm))

def check_fire(fire_status):
    global glo_fire_flag
    if fire_status  == 1:
        if glo_fire_flag == 0 :
            fire_alarm()
            glo_fire_flag = 1
    if fire_status  != 1:
        glo_fire_flag = 0

def check_people(people_status):
    global glo_people_flag
    if people_status  == 1:
        if glo_people_flag == 0 :
            peopledetec_alarm()
            glo_people_flag = 1
    if people_status  != 1:
        glo_people_flag = 0

def check_temp(temp_status,alarm_temp):
    global glo_temp_flag
    if temp_status  >= alarm_temp:
        if glo_temp_flag == 0 :
            Temperature_alarm()
            glo_temp_flag = 1
    if temp_status < alarm_temp :
        glo_temp_flag = 0

def jobforpublish():
    try:
        alarm_temp = 24
        #check people and fire status
        FirePeople_value = get_FirePeople()
        Fire_value = FirePeople_value[0]
        People_value = FirePeople_value[1]
        
        # Fire_status publish and alarm
        Fire_Func(Fire_value)
        check_fire(Fire_value)
        # peopledetec_status publish and alarm
        peopledetec_Func(People_value)
        check_people(People_value)
        
        # temperature value publish and alarm
        Evm_TH = get_temphumi()
        check_temp(Evm_TH[0],alarm_temp)
        print (Evm_TH)
        TempHumi(Evm_TH[0],Evm_TH[1])
    except:
        print ("somethingerror_normal")
    
    
def jobforalarm():
    try:
        alarm_temp = 25
        FirePeople_value = get_FirePeople()
        Fire_value = FirePeople_value[0]
        People_value = FirePeople_value[1]
        
        # Fire_status publish and alarm
        if Fire_value == 1:
            Fire_Func(Fire_value)
            check_fire(Fire_value)
        # peopledetec_status publish and alarm
        if People_value == 1:
            peopledetec_Func(People_value)
            check_people(People_value)
        
        # temperature value publish and alarm
        Evm_TH = get_temphumi()
        if Evm_TH[0] >= alarm_temp:
            check_temp(Evm_TH[0],alarm_temp)
            TempHumi(Evm_TH[0],Evm_TH[1])
    except:
        print ("somethingerror_alarm")
    
    # print (get_earthquake())
    
schedule.every(1).minutes.do(jobforpublish)  
schedule.every(1).seconds.do(jobforalarm)  


if __name__ == '__main__':  

    while True:  
        schedule.run_pending()  
        time.sleep(1) 

'''

if __name__ == '__main__':
    while True:
        print (get_FirePeople())
        print (get_temphumi())
        time.sleep(1)

if __name__ == '__main__':
    alarm_temp = 22
    while True:
        #print(get_ADAM())
        
        #check people and fire status
        FirePeople_value = get_FirePeople()
        Fire_value = FirePeople_value[0]
        People_value = FirePeople_value[1]
        
        # Fire_status publish and alarm
        Fire_Func(Fire_value)
        check_fire(Fire_value)
        # peopledetec_status publish and alarm
        peopledetec_Func(People_value)
        check_people(People_value)
        
        # temperature value publish and alarm
        Evm_TH = get_temphumi()
        check_temp(Evm_TH[0],alarm_temp)
        print (Evm_TH)
        TempHumi(Evm_TH[0],Evm_TH[1])
        
        
        
        
        time.sleep(5)

'''
       
        
        
        
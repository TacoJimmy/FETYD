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
glo_power_flag = 0
glo_water_flag = 0
glo_earth_flag  = 0

def MQTT_Connect():
    global client
    client = mqtt.Client()
    client.username_pw_set("acme","85024828")
    client.connect("210.68.227.123", 3881, 60)

def read_Main_PowerMeter(ID):
    try:
        master = modbus_rtu.RtuMaster(serial.Serial(port='/dev/ttyS1', baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
        master.set_timeout(5.0)
        master.set_verbose(True)
        MainPW_meter = [0,0,0,0,0,0,0,0,0]
        pw_va = master.execute(ID, cst.READ_HOLDING_REGISTERS, 311, 2)
        pw_cur = master.execute(ID, cst.READ_HOLDING_REGISTERS, 321, 2)
        pw_power = master.execute(ID, cst.READ_HOLDING_REGISTERS, 337, 2)
        pw_pf = master.execute(ID, cst.READ_HOLDING_REGISTERS, 358, 1)
        pw_consum = master.execute(ID, cst.READ_HOLDING_REGISTERS, 385, 2)
        pw_DM = master.execute(ID, cst.READ_HOLDING_REGISTERS, 362, 2)
        
        MainPW_meter[0] = round(pw_va[1] * 0.1,1)
        MainPW_meter[1] = round(pw_cur[1] * 0.001,1)
        MainPW_meter[2] = 0
        MainPW_meter[3] = 0
        MainPW_meter[4] = round((pw_power[0]*65535 + pw_power[1]) ,1)
        MainPW_meter[5] = round(pw_pf[0]*0.1,1)
        MainPW_meter[6] = round((pw_consum[0]* 65535 + pw_consum[1] )*0.1,1)
        MainPW_meter[7] = 1
        MainPW_meter[8] = round(((pw_DM[0] * 65535 + pw_DM[1])),1)
        master.close()
        
        return (MainPW_meter)
    except:
        print("error_ModbusRTU_PowerMaeter")
        master.close
        
        
def get_temphumi(ID):
    try:
        master = modbus_rtu.RtuMaster(serial.Serial(port='/dev/ttyS1', baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
        master.set_timeout(5.0)
        master.set_verbose(True)
        temp = master.execute(ID, cst.READ_HOLDING_REGISTERS, 3, 2) 
        evm_temp = round(temp[0]*0.01,1)
        evm_humi = round(temp[1]*0.01,1)
    
        return evm_temp,evm_humi
    except:
        print("error_ModbusRTU_temphumi")
        master.close
        

def get_earthquake():
    try:
        master = modbus_rtu.RtuMaster(serial.Serial(port='/dev/ttyS1', baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
        master.set_timeout(5.0)
        master.set_verbose(True)
        earth = master.execute(1, cst.READ_HOLDING_REGISTERS, 286, 2) 
        earth_level = round(earth[0])
        earth_value = round(earth[1])
    
        return earth_level,earth_value
    except:
        print("error_ModbusRTU_earthquake")
        master.close
        return (9,0)
        

def get_water():
    water_limit = 300
    try:
        master = modbus_rtu.RtuMaster(serial.Serial(port='/dev/ttyS1', baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0))
        master.set_timeout(5.0)
        master.set_verbose(True)
        earth = master.execute(20, cst.READ_HOLDING_REGISTERS, 282, 2) 
        water_level = round(earth[0])
        water_value = round(earth[1])

        if water_level >= water_limit :
            water_data = 0
        else:
            water_data = 1
    
        return water_data
    except:
        print("error_ModbusRTU_water")
        master.close
        pass





def setmqtt():
    glo_fire_flag = 0
    glo_people_flag = 0
    glo_temp_flag = 0
    client = mqtt.Client()
    client.username_pw_set("acme","85024828")
    client.connect("210.68.227.123", 3881, 60)

def get_FirePeople():
    try:
        Fire_status = 0
        People_status = 0
        ser = serial.Serial(port='/dev/ttyS4', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
        ser.write(b'$016\r\n') # send command for gate Di data
        output = str(ser.read(9)) # Read 9 bytes from serial buffer 
        FirePeople_status = int(output[4])

        if FirePeople_status & 2 == 2: #check Fire
            Fire_status = 1
        if FirePeople_status & 1 == 1: #check people detect
            People_status = 1
        
        return Fire_status,People_status
        
    except:
        print("error_ModbusASCII")
        ser.close

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
    
def Water_Func(water_level):
    payload_WaterNode = {"WaterNode_01":water_level}
    print (json.dumps(payload_WaterNode))
    client.publish("yuanta/water", json.dumps(payload_WaterNode))
    
def Fire_Func(fire_status):
    try:
        if fire_status == 1 :
            payload_fire = {"FireNode_01":0}
        elif fire_status == 0 :
            payload_fire = {"FireNode_01":1}
        print (json.dumps(payload_fire))
        client.publish("yuanta/fire", json.dumps(payload_fire))
    except:
        print ("can't publish Fire")

def peopledetec_Func(people_status):
    try:
        if people_status == 1 :
            payload_peopledetec = {"PeopleDetec":0}
        elif people_status == 0 :
            payload_peopledetec = {"PeopleDetec":1}
        print (json.dumps(payload_peopledetec))
        client.publish("yuanta/peopledetec", json.dumps(payload_peopledetec))
    except:
        print ("can't publish people detection")

def TempHumi(temp,humi):
    payload_TempHumi = {"Temperature":temp,"Humidity":humi}
    print (json.dumps(payload_TempHumi))
    client.publish("yuanta/th", json.dumps(payload_TempHumi))

def PowerManage(Powerdata):
    
    payload_power = {"mainpowertype":"單相單線",
                        "voltage":Powerdata[0],
                        "current_r":Powerdata[1],
                        "power":Powerdata[4],
                        "pf":Powerdata[5],
                        "energy":Powerdata[6],
                        "emsdevicealive":Powerdata[7],
                        "DM":Powerdata[8],
                        "loop_name":"mainpower",
                        }
    print (json.dumps(payload_power))
    client.publish("yuanta/electricity", json.dumps(payload_power))
    
def earthquake(earthquake_level, earthquake_value):
    payload_earthquake = {"earthquake":earthquake_level,"earthquake_value":earthquake_value,"sensor_alive":1}
    print (json.dumps(payload_earthquake))
    client.publish("yuanta/earthquake", json.dumps(payload_earthquake))
    
def earthquake_alarm():
    payload_earthquakealarm = {"earthquake_alarm":0}
    print (json.dumps(payload_earthquakealarm))
    print("earthquake_alarm")
    client.publish("yuanta/earthquake_error", json.dumps(payload_earthquakealarm))
    
def Temperature_alarm(temp):
    payload_temperaturealarm = {"Temperature":0}
    print (json.dumps(payload_temperaturealarm))
    print("Temperature_alarm")
    client.publish("yuanta/th_error", json.dumps(payload_temperaturealarm))

def Power_alarm(voltage_status):
    payload_voltagealarm = {"voltage_error_r":0}
    print (json.dumps(payload_voltagealarm))
    print("Power_alarm")
    client.publish("yuanta/electricity_error", json.dumps(payload_voltagealarm))

def Humidity_alarm(humi):
    payload_Humidityalarm = {"Humidity":humi}
    print (json.dumps(payload_Humidityalarm))
    client.publish("yuanta/th_error", json.dumps(payload_Humidityalarm))

def fire_alarm():
    payload_firealarm = {"FireNode_error_01":0}
    print (json.dumps(payload_firealarm))
    print("fire_alarm")
    client.publish("yuanta/fire_error", json.dumps(payload_firealarm))
    

def water_alarm():
    payload_wateralarm = {"WaterNode_error_01":0}
    print (json.dumps(payload_wateralarm))
    print("water alarm")
    client.publish("yuanta/water_error", json.dumps(payload_wateralarm))

def peopledetec_alarm():
    peopledetec_alarm = {"PeopleDetec_alarm":0}
    print (json.dumps(peopledetec_alarm))
    print ("peopledetec_alarm")
    client.publish("yuanta/peopledetec_error", json.dumps(peopledetec_alarm))

def check_fire(fire_status):
    global glo_fire_flag
    if fire_status  == 1:
        if glo_fire_flag == 0 :
            fire_alarm()
            Fire_Func(fire_status)
            glo_fire_flag = 1
    if fire_status  != 1:
        glo_fire_flag = 0

def check_people(people_status):
    global glo_people_flag
    if people_status  == 1:
        if glo_people_flag == 0 :
            peopledetec_alarm()
            peopledetec_Func(people_status)
            glo_people_flag = 1
    if people_status  != 1:
        glo_people_flag = 0

def check_temp(temp_status,humi_status,alarm_temp):
    global glo_temp_flag
    if temp_status  >= alarm_temp:
        if glo_temp_flag == 0 :
            Temperature_alarm(temp_status)
            TempHumi(temp_status,humi_status)
            glo_temp_flag = 1
    if temp_status < alarm_temp:
        glo_temp_flag = 0

def check_power(voltage_status,alarm_voltage,Powerdata):
    global glo_power_flag
    if voltage_status  <= alarm_voltage:
        if glo_power_flag == 0 :
            Power_alarm(voltage_status)
            PowerManage(Powerdata)
            glo_power_flag = 1
    if voltage_status > alarm_voltage:
        glo_power_flag = 0

def check_water(water_level):
    global glo_water_flag
    if water_level  == 0:
        if glo_water_flag == 0 :
            water_alarm()
            Water_Func(water_level)
            
            glo_water_flag = 1
    if water_level != 0:
        glo_water_flag = 0


def check_earthquake(earth_level):
    global glo_earth_flag
    if earth_level  >= 5:
        if glo_earth_flag == 0 :
            earthquake_alarm()
            earthquake(earth_level)
            print ("earthquake")
            glo_earth_flag = 1
    if earth_level == 0:
        glo_earth_flag = 0


def jobforpublish():
    try:
        
        # publish power data
        Powerdata = read_Main_PowerMeter(5) #PowerMeter ID = 5
        PowerManage(Powerdata)
        
        # publish temperature and humidity
        Evm_TH = get_temphumi(10)
        TempHumi(Evm_TH[0],Evm_TH[1])
        
        # publish People Detect and fire status
        FirePeople_value = get_FirePeople()
        Fire_Func(FirePeople_value[0]) #FirePeople_value[0] = fire status
        peopledetec_Func(FirePeople_value[1]) #FirePeople_value[0] = people detect status
        
        # get water
        water_level = get_water()
        Water_Func(water_level)
        
        # get earth_level
        earth_level = get_earthquake()
        time.sleep(0.5)
        earthquake(earth_level[1],earth_level[0])

    except:
        print ("somethingerror_normal")
    
def jobforalarm():
    try:
        
        # temperature alarm
        alarm_temp = 28
        Evm_TH = get_temphumi(10)
        check_temp(Evm_TH[0],Evm_TH[1],alarm_temp)
        
        # Fire_status and people_status alarm
        FirePeople_value = get_FirePeople()
        check_fire(FirePeople_value[0])
        check_people(FirePeople_value[1])
        
        # water_status alarm
        water_level = get_water()
        check_water(water_level)
        
        # power_status alarm
        Powerdata = read_Main_PowerMeter(5)
        check_power(Powerdata[0],100,Powerdata)
        
        
        # earthquake_status alarm
        earth_level = get_earthquake()
        check_earthquake(earth_level[1])

    except:
        print ("somethingerror_alarm")


schedule.every(30).seconds.do(jobforpublish)  
schedule.every(1).seconds.do(jobforalarm)  


if __name__ == '__main__':  
    
    MQTT_Connect()
    
    while True:  
        '''
        print (get_earthquake())
        
        print (read_Main_PowerMeter(5))
        print (get_water())
        print (get_temphumi(10))
        print (get_FirePeople())
        time.sleep(2)
        '''
        
        schedule.run_pending()  
        time.sleep(1) 
        
    
    
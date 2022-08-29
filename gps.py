#!/usr/bin/env python
# -*- coding: utf-8 -*-
from statistics import mean
import serial
import operator
import collections
import calcpoint
import math
from functools import reduce
import numpy as np
from adafruit_servokit import ServoKit
import time

ser = serial.Serial(port = "/dev/ttyACM0", baudrate = 38400, timeout = 0.1)    
kit = ServoKit(channel=27)
kit2 = ServoKit(channel=19)

hopping_count = 0
def GPSparser(data):
	gps_data = data.split(b",")
	idx_rmc = data.find(b'GNGGA')
	if data[idx_rmc:idx_rmc+5] == b"GNGGA":
		data = data[idx_rmc:]    
		if checksum(data):
		   # print(data)
			parsed_data = data.split(b",")
			print(parsed_data)
			return parsed_data
		else :
			print ("checksum error")

def checksum(sentence):
	sentence = sentence.strip(b'\n')
	nmeadata, cksum = sentence.split(b'*',1)
	calc_cksum = reduce(operator.xor, (ord(chr(s)) for s in nmeadata), 0)
	print(int(cksum,16), calc_cksum)
	if int(cksum,16) == calc_cksum:
		return True 
	else:
		return False 

def Optimal(lat_1,lon_1,lat_2,lon_2):
    optimal = 199.798876356 - (math.atan((lon_2-lon_1)/(lat_2-lat_1)) * 180 / math.pi +180)
    print('cool: %f' %(optimal))
    return optimal

def location():
	
    data = ser.readline()
    result = collections.defaultdict()
    res = GPSparser(data)
    if res == None:
        return(0,0)
    else:
        print(res)
        lat = str (res[2])
        lon = str (res[4])
        if (res == "checksum error"):
            print("")
            print(lat)
        else:
            lat_h = float(lat[2:4])
            lon_h = float(lon[2:5])
            lat_m = float(lat[4:12])
            lon_m = float(lon[5:13])
            print('lat_h: %f lon_h: %f lat_m: %f lon_m: %f' %(lat_h, lon_h, lat_m, lon_m))
            latitude = lat_h + (lat_m/60)
            longitude = lon_h + (lon_m/60)
            print('latitude: %f longitude: %f' %(latitude,longitude))

    return latitude,longitude
    # Optimal(latitude,longitude,first_lon)


hopping_count = 0
points = [[35.232104,129.079300],[35.232070,129.079251]]

def locationForAngle():
    if hopping_count == 2:
        return
    sum = 0
    cnt = 1
    while True:
        data = ser.readline()
        result = collections.defaultdict()
        res = GPSparser(data)
        if res == None:
            continue
        else:
            print(res)
            lat = str (res[2])
            lon = str (res[4])
            if (res == "checksum error"):
                print("")
                print(lat)
            else:
                if cnt%5 == 0:
                    Servo(sum/5)
                lat_h = float(lat[2:4])
                lon_h = float(lon[2:5])
                lat_m = float(lat[4:12])
                lon_m = float(lon[5:13])
                print('lat_h: %f lon_h: %f lat_m: %f lon_m: %f' %(lat_h, lon_h, lat_m, lon_m))
                latitude = lat_h + (lat_m/60)
                longitude = lon_h + (lon_m/60)
                print('latitude: %f longitude: %f' %(latitude,longitude))
                sum += Optimal(latitude,longitude,points[hopping_count][0],points[hopping_count][1])
                cnt += 1

def Servo(angle):
    kit.servo[0].angle = angle
    kit2.continuous_servo[1].throttle = 1
    time.sleep(1)
    kit.servo[0].angle = 90
    locationForRange(angle)

def locationForRange(angle):
    latitude = points[hopping_count][0]
    longitude = points[hopping_count][1]
    while True:
        data = ser.readline()
        result = collections.defaultdict()
        res = GPSparser(data)
        if res == None:
            continue
        else:
            print(res)
            lat = str (res[2])
            lon = str (res[4])
            if (res == "checksum error"):
                print("")
                print(lat)
            else:
                lat_h = float(lat[2:4])
                lon_h = float(lon[2:5])
                lat_m = float(lat[4:12])
                lon_m = float(lon[5:13])
                print('lat_h: %f lon_h: %f lat_m: %f lon_m: %f' %(lat_h, lon_h, lat_m, lon_m))
                latitude = lat_h + (lat_m/60)
                longitude = lon_h + (lon_m/60)
                print('latitude: %f longitude: %f' %(latitude,longitude))
                range = 6 * math.sqrt((lat-latitude)*(lat-latitude)+(lon-longitude)(lon-longitude)) / math.sqrt(0.000049*0.000049+0.000018*0.000018)
                if (range < 1):
                    kit2.continuous_servo[1].throttle = 0
                    locationForAngle(angle)
                    hopping_count -= 1



        
if __name__ == '__main__':
    print("##################")
    print(get())

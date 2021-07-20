#-----------------------------------------------------------------------------------------------------------
#This app will serve as the backend for the flask app which will take the lidar readings and save them until
#a get request is issued. After the get request the queue of readings will clear itself and then save more
#readings.
#-----------------------------------------------------------------------------------------------------------
import RPi.GPIO as gpio
import time
from math import ceil, floor
from lidar_lite import Lidar_Lite
from flask import Flask, jsonify
import numpy
import nvector as nv
import pigpio
from pymavlink import mavutil, mavlink
app = Flask(__name__)
lidar = Lidar_Lite()
#connect to lidar device
connected = lidar.connect(1)
#This list will serve as out readings queue
distanceReadings = []
#stepRate is how much the signal will have to increase/decrease by to move the servo one degree
stepRate = 22.222222222222
pi = pigpio.pi()
GPIO = 17
#Make sure that the device is actually connected and print out an appropriate message
if connected < -1 or not pi.connected:
    print("Error, Either lidar or pigpio not connected (maybe try running the pigpio daemon")
else:
    print("Both Lidar and Pigpio connected")
#connect to the flight controller through the rasp pi's USB port (ttyACM0) MAY STILL TRY TO FIND WAY TO GET TELEMETRY
#TO WORK BUT WE'LL SEE
mavlinkConnection = mavutil.mavlink_connection('/dev/ttyACM0', baudrate = 921000)
#check to make sure you get a heartbeat from the flight controller
mavlinkConnection.wait_heartbeat()
if mavlinkConnection.target_system != 1:
    print('Error: Could not connect to the Flight Controller')
#Before the very first get request is issued get irst readings
@app.before_first_request
def firstRunThrough():
    pi.set_servo_pulsewidth(17, 500)
    goUp(pi)
    goDown(pi)
#After every other subsequent get request, clear the queue and then put new readings into the queue
@app.after_request
def after_request_func(response):
    global recordCount
    recordCount = 0
    distanceReadings.clear()
    goUp(pi)
    goDown(pi)
    return response

#calculate the latitude, longitude from the distance measurement and return a dictionary. This will be what is put into
#the queue of readings
def positionCalculator(altitude, lat,long, distCm, azimuth, bruh):
    frame = nv.FrameE(a = altitude, f = 0)
    pointA = frame.GeoPoint(latitude = lat, longitude = long, degrees = True)
    distM = distCm / 100
    pointB, azimuth = pointA.displace(distance = distM, azimuth = azimuth, degrees = True)
    returnDict = {
        "latitude": pointB.latitude_deg,
        "longitude": pointB.longitude_deg,
        "distance" : distCm,
        "alt": altitude
    }
    return returnDict
#send signals to the servo to go from 0 degrees (500 pwm) to 180 degrees (2500 pwm) and take a reading at every
#degree.
def goUp(pi):
    #start at 0 degrees
    signal = 500
    global recordCount
    #go until you hit 180 degrees
    while signal < 2500:
        #send signal to the servo to go up one more degree
        pi.set_servo_pulsewidth(17, floor(signal))
        #get the altitude from the flight controller. This will be used in the latitude/longitude coordinate
        #calculations
        alt = float(mavlinkConnection.recv_match(type = 'GLOBAL_POSITION_INT', blocking = True).alt) / 1000
        #take a distance measurement and add it to the distance readings array
        distanceReadings.append(positionCalculator(alt, 80, -90, lidar.getDistance(0), 200, alt))
        time.sleep(.005)
        #increment the signal by one
        signal = signal + stepRate
#send signals to the servo to go from 180 degrees (2500 pwm) to 0 degrees (500 pwm) and take a reading at every
#degree.
def goDown(pi):
    #start at 180 degrees
    signal = 2500
    global recordCount
    #go until you hit 0 degrees
    while signal > 500:
        #send signal to the servo to do down by one more degree
        pi.set_servo_pulsewidth(17, floor(signal))
        #get the altitude from the flight controller. This will be used for the lat/long calculations
        alt = float(mavlinkConnection.recv_match(type = 'GLOBAL_POSITION_INT', blocking = True).alt) / 1000
        #take a lidar distance reading
        distanceReadings.append(positionCalculator(alt, 80, -90, lidar.getDistance(0), 200, alt ))
        time.sleep(.005)
        #decrement the signal by one
        signal = signal - stepRate
#upon a get request return the readings queue
@app.route('/', methods = ['POST', 'GET'])
def getReadings():
    return jsonify(distanceReadings)
#run the app
if __name__ == '__main__':
    app.debug = True
    #request that the positional data (GLOBAL_POSITION_INT) be sent at a higher rate. NOTE MAY TAKE THIS OUT SINCE I
    #DONT THINK IT ACTUALLY HELPS AT ALL
    mavlinkConnection.mav.request_data_stream_send(mavlinkConnection.target_system, mavlinkConnection.target_component, mavutil.mavlink.MAV_DATA_STREAM_POSITION, 500, 1)
    print("Heartbeat from system (system %u component %u" % (mavlinkConnection.target_system, mavlinkConnection.target_component))
    app.run()

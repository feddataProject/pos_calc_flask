#-----------------------------------------------------------------------------------------------------------
#This app will serve as the backend for the flask app which will take the lidar readings and save them until
#a get request is issued. After the get request the queue of readings will clear itself and then save more
#readings.
#-----------------------------------------------------------------------------------------------------------
import RPi.GPIO as gpio
import time
from math import ceil
from lidar_lite import Lidar_Lite
from flask import Flask, jsonify, copy_current_request_context
import numpy
import nvector as nv
import pigpio
app = Flask(__name__)
lidar = Lidar_Lite()
#connect to lidar device
connected = lidar.connect(1)
#This list will serve as out readings queue
distanceReadings = []
takeNap = 0
stepRate = 12.222222222222
pi = pigpio.pi()
GPIO = 17
#Make sure that the device is actually connected and print out an appropriate message
if connected < -1 or not pi.connected:
    print("Error, Either lidar or pigpio not connected (maybe try running the pigpio daemon")
else:
    print("Both Lidar and Pigpio connected")
#Before the very first get request is issued get irst readings
@app.before_first_request
def firstRunThrough():
    pi.set_servo_pulsewidth(17, 500)
    goUp(pi)
    goDown(pi)
#After every other subsequent get request, clear the queue and then put new readings into the queue
@app.after_request
def after_request_func(response):
    print("Before Clear: ", len(distanceReadings))
    distanceReadings.clear()
    goUp(pi)
    goDown(pi)
    return response
#calculate the latitude, longitude from the distance measurement and return a dictionary. This will be what is put into
#the queue of readings
def positionCalculator(altitude, lat,long, distCm, azimuth):
    frame = nv.FrameE(a = altitude, f = 0)
    pointA = frame.GeoPoint(latitude = lat, longitude = long, degrees = True)
    distM = distCm / 100
    pointB, azimuth = pointA.displace(distance = distM, azimuth = azimuth, degrees = True)
    returnDict = {
        "latitude": pointB.latitude_deg,
        "longitude": pointB.longitude_deg,
        "distance" : distCm
    }
    return returnDict
#send signals to the servo to go from 0 degrees (500 pwm) to 180 degrees (2500 pwm) and take a reading at every
#degree.
def goUp(pi):
    #start at 0 degrees
    signal = 500
    #go until you hit 180 degrees
    while signal < 2500:
        #send signal to the servo to go up one more degree
        pi.set_servo_pulsewidth(17, ceil(signal))
        #take a lidar distance reading
        distanceReadings.append(positionCalculator(6371e3, 80, -90, lidar.getDistance(0), 200))
        #increment the signal by one
        signal = signal + stepRate
    #afterwords take a short breather before going back down. NOTE: MAY TAKE THIS OUT
    #time.sleep(.05)
#send signals to the servo to go from 180 degrees (2500 pwm) to 0 degrees (500 pwm) and take a reading at every
#degree.
def goDown(pi):
    #start at 180 degrees
    signal = 2500
    #go until you hit 0 degrees
    while signal > 500:
        #send signal to the servo to do down by one more degree
        pi.set_servo_pulsewidth(17, ceil(signal))
        #take a lidar distance reading
        distanceReadings.append(positionCalculator(6371e3, 80, -90, lidar.getDistance(0), 200))

        #decrement the signal by one
        signal = signal - stepRate
    #take a short breather before going back Up NOTE: MAY TAKE THIS OUT
    #time.sleep(.05)
#upon a get request return the readings queue
@app.route('/', methods = ['POST', 'GET'])
def getReadings():
    return jsonify(distanceReadings)
#run the app
if __name__ == '__main__':
    app.debug = True
    app.run()

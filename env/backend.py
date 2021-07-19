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
    goDown(pi)
    goUp(pi)
#After every other subsequent get request, clear the queue and then put new readings into the queue
@app.after_request
def after_request_func(response):
    print("Before Clear: ", len(distanceReadings))
    distanceReadings.clear()
    print("\n\n\n\n\n\n\nClearing queue, queue size is now: ", len(distanceReadings))
    goDown(pi)
    goUp(pi)
    return response

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
def goDown(pi):
    signal = 500
    while signal < 2500:
        pi.set_servo_pulsewidth(17, ceil(signal))
        distanceReadings.append(lidar.getDistance(0))
        signal = signal + stepRate
    time.sleep(.05)
def goUp(pi):
    signal = 2500
    while signal > 500:
        pi.set_servo_pulsewidth(17, ceil(signal))
        distanceReadings.append(lidar.getDistance(0))
        signal = signal - stepRate
    time.sleep(.05)
#upon a get request return the readings queue
@app.route('/', methods = ['POST', 'GET'])
def getReadings():
    return jsonify(distanceReadings)
#run the app
if __name__ == '__main__':
    app.debug = True
    app.run()

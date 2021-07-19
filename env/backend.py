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
app = Flask(__name__)
lidar = Lidar_Lite()

#connect to lidar device
connected = lidar.connect(1)
#This list will serve as out readings queue
distanceReadings = []
takeNap = 0
#Make sure that the device is actually connected and print out an appropriate message
if connected < -1:
    print("Error, not Connected")
else:
    print("connected")
#Before the very first get request is issued get irst readings
@app.before_first_request
def firstRunThrough():
    count = 0
    while count < 180:
        distanceReadings.append(positionCalculator(6371e3, 80, -90, lidar.getDistance(0), 200))
        count+=1
#After every other subsequent get request, clear the queue and then put new readings into the queue
@app.after_request
def after_request_func(response):
    print("Before Clear: ", len(distanceReadings))
    distanceReadings.clear()
    print("\n\n\n\n\n\n\nClearing queue, queue size is now: ", len(distanceReadings))
    count = 0
    while count < 180:
        distanceReadings.append(positionCalculator(6371e3, 80, -90, lidar.getDistance(0), 200))
        count+=1
    return response

def positionCalculator(altitude, lat,long, distCm, azimuth):
    frame = nv.FrameE(a = altitude, f = 0)
    pointA = frame.GeoPoint(latitude = lat, longitude = long, degrees = True)
    distM = distCm / 100
    pointB, azimuth = pointA.displace(distance = distM, azimuth = azimuth, degrees = True)
    returnDict = {
        "latitude": pointB.latitude_deg,
        "longitude": pointB.longitude_deg
    }
    return returnDict
#upon a get request return the readings queue
@app.route('/', methods = ['POST', 'GET'])
def getReadings():
    return jsonify(distanceReadings)
#run the app
if __name__ == '__main__':
    app.debug = True
    app.run()

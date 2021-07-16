import numpy as np  
import nvector as nv   

def posCalc(altitude, lat, long, dis_cm, azimuth):
    frame = nv.FrameE(a = altitude, f = 0)
    pointA = frame.GeoPoint(latitude=lat, longitude=long, degrees=True)
    dis_m = dis_cm/100
    pointB, azimuthB = pointA.displace(distance=dis_m, azimuth=azimuth, degrees=True)
    return_dict = {
        "latitude": pointB.latitude_deg,
        "longitude":pointB.longitude_deg
    }
    return return_dict




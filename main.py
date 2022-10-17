import network
import socket
from time import sleep
import machine
import urequests
import picographics
import jpegdec
from secrets import secrets
from pimoroni import RGBLED, Button
import haversine

display = picographics.PicoGraphics(display=picographics.DISPLAY_ENVIRO_PLUS)
black_pen = display.create_pen(0, 0, 0)
white_pen = display.create_pen(255, 255, 255)
red_pen = display.create_pen(255, 0, 0)
pink_pen = display.create_pen(251,72,196)
led = RGBLED(6, 7, 10, invert=True)

def connect():
    #Connect to WLAN
    led.set_rgb(255, 0, 0)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets['ssid'], secrets['password'])
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    led.set_rgb(0, 255, 0)
    return ip

try:
    ip = connect()
except KeyboardInterrupt:
    machine.reset()

def iss_lat_lon():
    JSON_URL = "http://api.open-notify.org/iss-now.json"
    try:
        result = urequests.get(JSON_URL).json()["iss_position"]
    except RuntimeError as r:
        wifi.disconnect()
        ip = connect()
        result = urequests.get(JSON_URL).json()["iss_position"]
    lat = result["latitude"]
    lon = result["longitude"]
    return lat,lon

def CalcLoc(iss):
    d = haversine.distance((float(51.4780),float(0.0015)),(float(iss[0]),float(iss[1])))
    citydist = d
    return (round(citydist,2))

def mapdot(self):
 #position of red dot on mini map
 y = round(180-(float(self[0])+90))
 x = round(float(self[1])+180)
 return [y,x]

def main():
    trail = []
    t = 0
    while True:
        led.set_rgb(0, 0, 0)
        iss_yx = iss_lat_lon()
        loc = CalcLoc(iss_yx)
        mapyx = mapdot(iss_yx)
        if mapyx[1] > 180:
            mapshift = -120
            mapmove = 1
        else:
            mapshift = 0
            mapmove = 0
        display.set_pen(black_pen)
        display.clear()
        #display map
        j = jpegdec.JPEG(display)
        j.open_file("worldmap360-4bit-rle.jpg")
        j.decode(mapshift, 0, jpegdec.JPEG_SCALE_FULL)
        display.set_font("bitmap8")
        display.set_pen(pink_pen)
        display.circle(180+mapshift,39,2)
        display.set_pen(white_pen)
        display.text(str("Greenwich Meridian is:"), 0, 190, scale=2)
        display.text(str(str(loc) + "km from the ISS"), 0, 210, scale=2)
        display.set_pen(red_pen)
        display.circle(mapyx[1]+mapshift,mapyx[0],4)
        if mapmove == 1:
            for i in trail:
                display.circle(i[0]+mapshift,i[1], 2)
        else:
            for i in trail:
                display.circle(i[0],i[1], 2)
        display.update()
        if len(trail) >= 30:
            trail.pop(0)
        if t == 0:
            trail.append((int(mapyx[1]), int(mapyx[0])))
            t = 4
        else:
            t -= 1
        sleep(30) #wait 30 seconds *minimum time 5 seconds*

if __name__ == "__main__":
    main()  

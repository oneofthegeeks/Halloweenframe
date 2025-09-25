#!/usr/bin/python
import subprocess as sp
import time
import os
import datetime
from pirDetect import *
import sys

video = ["omxplayer", "filename", "-o", "both", "--win", "0 0 1280 720", "--aspect-mode", "fill", "--no-osd", "--orientation" ,"180","--vol", "-600"]
record = ["raspivid", "-o", "filename", "-n", "-t", "5000", "-rot","180"]
scareFile = "/home/pi/Projects/Halloween/ScareMedia/{0}ScareV.mp4".format(sys.argv[1])

def getFileName():
    return "/home/pi/Projects/Halloween/Recordings/" + datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")

def subProcWait(params):
        sub = sp.Popen(params)
        while sub.poll() is None:
            time.sleep(.1)

def onMotion(currState):
    if currState:
        autoFileName = getFileName()  # Get a time stamped file name
        record[2] = autoFileName
        subRecord = sp.Popen(record)  # Start recording to capture their fright
        video[1] = scareFile
        subProcWait(video)  # Play the video to scare them
        video[1] = autoFileName
        subProcWait(video)  # Play back the video we just recorded

def showImage():
    os.system("sudo fbi -T 1 -d /dev/fb0 -noverbose -once /home/pi/Projects/Halloween/ScareMedia/{0}Start.png".format(
        sys.argv[1]))


showImage()
objDetect = detector(7)
objDetect.subscribe(onMotion)
objDetect.start()
os.system("sudo killall -9 fbi")
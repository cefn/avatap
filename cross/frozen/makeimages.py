#!/usr/bin/python3

import os,sys
from subprocess import check_output

scriptPath = os.path.realpath(__file__)

# Start in script current directory
os.chdir(os.path.dirname(scriptPath))

# prepare paths
gitFolder = os.path.realpath("../../../")
loaderPath = os.path.join(gitFolder, "avatap/python/loader.py")
buildPath = os.path.join(gitFolder, "micropython/esp8266/build/firmware-combined.bin")

imageName = "hyperloop"

boxCounts = dict(
	arbeia=3,
	corbridge=4,
	#housesteads=4,
	segedunum=4,
	senhouse=3,
	TullieHouse=4,
)

def call(command):
	sys.stdout.write(check_output(command).decode("ascii"))

def replaceall(pattern, replacement, filepath):
	call(["perl", "-pi", "-E", "s/{}/{}/g".format(pattern, replacement),  filepath])

for museumName,boxCount in boxCounts.items():
	replaceall("storyUid.*=.*$", "storyUid = '{}'".format(museumName), loaderPath)
	for boxName in range(boxCount):
		boxName = boxName + 1 # cardinal numbers
		boxPath = os.path.join(gitFolder,"avatap/firmware", museumName, "{}{}.bin".format(imageName, boxName))
		replaceall("boxUid.*=.*$", "boxUid = '{}'".format(boxName), loaderPath)
		#os.remove(buildPath)
		call(["rm", buildPath])
		call(["./export.sh"])
		#os.copyfile(buildPath, boxPath)
		call(["cp", buildPath, boxPath])

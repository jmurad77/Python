import time
from timeit import default_timer as timer
import threading
import json
import os

class PerformanceTimer:
    myStartTimer = timer()
    myEndTimer = timer()
    myTimeDiff = 0.0

    def StartTimer(self):
        self.myStartTimer = timer()

    def EndTimer(self):
        self.myEndTimer = timer()
        self.myTimeDiff = (self.myEndTimer - self.myStartTimer)

    def GetTimeDifference(self):
        return self.myTimeDiff
    
    def GetStartTime(self):
        return self.myStartTimer
    
    def PrintTimeDiff(self):
        print(self.myTimeDiff)


timeP = PerformanceTimer()
timeP.StartTimer()
weatherFile = open('weather_stations_10Mb.csv', 'r')

# first two lines are comments
weatherFile.readline()
weatherFile.readline()
 
line = weatherFile.readline() 
weatherDict = {}
while line:
	city,floatTemp = line.split(";",1)
	floatTemp = float(floatTemp)

	if city in weatherDict.keys():
		# do avg
		pastResults = weatherDict[city]

		# if current min is less, than replace old min
		if pastResults[0] > floatTemp:
			pastResults[0] = floatTemp

		# if current max is greater, replace old max
		if pastResults[2] < floatTemp:
			pastResults[2] = floatTemp

		# get a cumulative total to calucate avg later
		pastResults[1] += floatTemp

		# add one to total count of entries
		pastResults[3] += 1

		weatherDict[city] = pastResults
	else:
		# add first entry of dictionary
		# Min, Mean, Max, numberOfEntries
		weatherDict[city] = [floatTemp, floatTemp, floatTemp, 1]

	line = weatherFile.readline() 

fileOutput = open('output.csv', 'w')
for key, value in sorted(weatherDict.items()):
	results = weatherDict[key]
	# calucate the avg
	results[1] = results[1] / results[3]
	formatedOutput = "{};{:.4f};{:.4f};{:.4f}\n".format(key,results[0], results[1], results[2])
	fileOutput.write(formatedOutput)

fileOutput.close()

timeP.EndTimer()
timeP.PrintTimeDiff()
	
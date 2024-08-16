from timeit import default_timer as timer
import threading
import json
import os

def CalPrintout(perfTimer, report):
    perfTimer.StartTimer()
    counter = 0
    while counter < 100000:
        print(69.69 * counter)
        counter += 1
    perfTimer.EndTimer()
    report.AddTimingParameters(threading.current_thread().name, 
                               "PyTimer", 
                               threading.current_thread().ident, 
                               perfTimer.GetStartTime(),
                               perfTimer.GetTimeDifference())
        
class JsonTimeReport:
    jsonReportArray = []
    myLock = threading.Lock()
    jsonReportFile = os.getcwd() + "//TimingReport.json"
    
    def AddTimingParameters(self, name, category, pId, startTimer, timeDiff):
        self.myLock.acquire()
        jsonTrace = {
            "name" : name,
            "cat" : category,
            "ph" : "X",
            "ts" : (startTimer * 1000000),
            "dur" : (timeDiff * 1000000),
            "pid" : pId,
            "tid" : pId
        }
        self.jsonReportArray.append(jsonTrace)
        self.myLock.release_lock()
        
    def PrintTimingToJsonFile(self):
        jsonFinalOutput = {"schemaVersion" : 1,
                           "traceEvents" : self.jsonReportArray, 
                           #"displayTimeUnit" : "ms",
                           "traceName" : "TimingReport.json"
                           }
        file = open(self.jsonReportFile, "w")
        json.dump(jsonFinalOutput, file, indent=4)        
        file.close()
    
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

timing_1 = PerformanceTimer()
timing_2 = PerformanceTimer()
timing_3 = PerformanceTimer()
timing_4 = PerformanceTimer()
report = JsonTimeReport()

t1 = threading.Thread(target=CalPrintout, args=(timing_1, report,), name='Thread 1')
t2 = threading.Thread(target=CalPrintout, args=(timing_2, report,), name='Thread 2')
t3 = threading.Thread(target=CalPrintout, args=(timing_3, report,), name='Thread 3')
t4 = threading.Thread(target=CalPrintout, args=(timing_4, report,), name='Thread 4')

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()

report.PrintTimingToJsonFile()
print("DONE!")

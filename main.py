#!/usr/bin/env python

import pigpio
import time
import wavegenerator as wg
import sys
import glob, os

#for time calcultions
current_milli_time = lambda: int(round(time.time() * 1000))

Class machine:

    def __init__(self):
        #setup pi
        print("Initializing gpio ports")
        pi = pigpio.pi()
        pi.set_mode(wg.GPIOxdir, pigpio.OUTPUT)
        pi.set_mode(wg.GPIOydir, pigpio.OUTPUT)
        pi.set_mode(wg.GPIOxpul, pigpio.OUTPUT)
        pi.set_mode(wg.GPIOypul, pigpio.OUTPUT)
        self.pi = pi

    def close(self):
        print("Closing gpio ports")
        self.pi.stop()

    def startexp(self, filepath):
        os.chdir("/mydir")
        for f in glob.glob("*.gc"):
            print(f)
            #alter so this just runs before each file?
            preprocess(f)

    def preprocess(self, f):
        #create waveforms
        self.w = wg.Waves()

        self.f = f

        print("Pre-processing file:" + f)
        start_time = current_milli_time()

        #pre-process waves:
        #generate waves for each command head of time
        with open(f) as fh:
            for line in f:
                #ignore comments and blank lines
                if len(line) > 0 and line[0] != "#":

                    self.w.addgc(line) #add each line as gcode

        end_time = current_milli_time()
        print(["Preprcessing took", end_time-start_time, "ms"])

    #run on neural input data
    def process(self):
       print("Running file" + f)
       start_time = current_milli_time()
       print(["Began at", start_time])



       for wave in self.w.waves:
        n = int(wave[4])

        #xpul, ypul, xdir, ydir
        wave = wave[0:3]
        if (len(wave[0]) > 0):
            i = 0

            #this might be added to pre-processing
            #due to the delay between waves to interpolate them
            for each in wave:
                if (each != -1):
                    #add each usable wave
                    self.pi.wave_add_generic(each)

            #generate the resultant wave
            wid = pi.wave_create()
            for i in range(0, n-1):
                #send wave to socket
                self.pi.wave_send_once(wid)

                #replace with encoder reading:
                time.sleep(float(pi.wave_get_micros()) / 1000000)
            self.pi.wave_delete(wid)

        #send TTL pulse for finished

        print("Finished running file")

                

if __name__ == "__main__":
    gc = sys.argv[1]
       
    m = new Machine()
    
    f = open("exp/example.gc", "w")
    f.write(gc)

    #these should be done on triggers
    m.startexp("exp")
    m.process()
    m.close()

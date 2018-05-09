#!/usr/bin/env python

import pigpio
import time
import wavegenerator as wg
import sys

if __name__ == "__main__":
    gc = sys.argv[1]
    w = wg.Waves() 
    print(["GCODE", gc])
    w.addgc(gc)


    pi = pigpio.pi()
    pi.set_mode(wg.GPIOxdir, pigpio.OUTPUT)
    pi.set_mode(wg.GPIOydir, pigpio.OUTPUT)
    pi.set_mode(wg.GPIOxpul, pigpio.OUTPUT)
    pi.set_mode(wg.GPIOypul, pigpio.OUTPUT)

    for wave in w.waves:
        #print(["Num of waves:", len(wave)])
        n = int(wave[4])
        wave = wave[0:3]
        #print(["length of wave:", len(wave[0])])
        if (len(wave[0]) > 0):
            i = 0
            for each in wave:
                if (each != -1):
                    pi.wave_add_generic(each)
            wid = pi.wave_create()
            for i in range(0, n-1):
                pi.wave_send_once(wid)
                time.sleep(float(pi.wave_get_micros()) / 1000000)
            pi.wave_delete(wid)

    pi.stop()
       

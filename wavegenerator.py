import string
import math
import pigpio
GPIOxpul = 19
GPIOxdir = 13
GPIOypul = 16
GPIOydir = 20

PI = math.pi

convert = 1.0/60000000.0
microstep = 5.0
mmperrev = 70.0
pulseperrev = 200.0
mmperstep = mmperrev/(pulseperrev*microstep)


def frange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

def combinewave(wave, p):
    for w in wave:
        if (w != -1):
            p.wave_add_generic(w)
    return p


class Waves:
        def __init__(self):
                self.waves = [] #list of waves for given group
                self.maxf = 1 #max feedrate
                self.x = 0.0
                self.y = 0.0

        def addgc (self, gcline):
            splitgc = gcline.split(" ")
            for value in splitgc:
                if "G" in value:
                    cmd = int(self.toNum(value))
                if "X" in value:
                    xpos = self.toNum(value)
                if "Y" in value:
                    ypos = self.toNum(value)
                if "A" in value:
                    ampl = self.toNum(value)
                if "T" in value:
                    peri = self.toNum(value)
                if "N" in value:
                    numpulses = self.toNum(value)
                if "F" in value:
                    feedrate = self.toNum(value)

            #to add: error checking

            if cmd is 0:
                feedrate = self.maxf
            if cmd is 0 or cmd is 1:
                self.generatelinear(xpos, ypos, feedrate)
            if cmd is 83:
                self.generatesine(ampl, peri, feedrate, numpulses)

        def generatelinear(self, xpos, ypos, feedrate):

            F = feedrate * convert

            #change to separate y and x pulse sizes
            dely = ypos - self.y
            delx = xpos - self.x

            theta = math.atan2(dely, delx)
            vy = abs(F*math.sin(theta))
            vx = abs(F*math.cos(theta))



            #get lcd
            if (vx != 0):
                usperstepx = int(round(mmperstep / (2.0*vx))*2)
                dt = usperstepx
            elif (vy != 0):
                usperstepy = int(round(mmperstep / (2.0*vy))*2)
                dt = usperstepy
            print("usperstes:")


            totaltime = int(round((math.sqrt(dely*dely + delx*delx) / F)))
            n = round(totaltime / dt)


            totaltime = dt
            print("Time:")
            print(totaltime)

            #get pulse trains
            xpulwave = []
            ypulwave = []
            xdirwave = []
            ydirwave = []
            if (xpos != 0):
                for i in range (0, totaltime, usperstepx):
                    xpulwave.append(pigpio.pulse(1<<GPIOxpul, 0, int(usperstepx/2)))
                    xpulwave.append(pigpio.pulse(0, 1<<GPIOxpul, int(usperstepx/2)))
                if (xpos < 0):
                    xdirwave.append(pigpio.pulse(1<<GPIOxdir, 0, int(totaltime)))
                else:
                    xdirwave.append(pigpio.pulse(0, 1<<GPIOxdir, int(totaltime)))
            else:
                xpulwave = -1
                ydirwave = -1
            if (ypos != 0):
                for i in range(0, totaltime, usperstepy):
                    ypulwave.append(pigpio.pulse(1<<GPIOypul, 0 , int(usperstepy/2)))
                    ypulwave.append(pigpio.pulse(0, 1<<GPIOypul, int(usperstepy/2)))
                if (ypos < 0):
                    ydirwave.append(pigpio.pulse(1<<GPIOydir, 0, int(totaltime)))
                else:
                    ydirwave.append(pigpio.pulse(0, 1<<GPIOydir,int(totaltime)))
            else:
                ypulwave = -1
                ydirwave = -1

	                    
            self.waves.append([xpulwave, ypulwave, xdirwave, ydirwave, n])

        #generate sine pulses with constant feed rate
        #A := Magnitude in mm
        #T := Period in mm
        #F := Feed rate in mm/min
        #n := number of pulses to do (unitless)
        #Issue: pigpio limits the number of bytes in pulse trains
        #this may mean breaking up waves into multiple segments or losing resolution
        def generatesine(self, A, T, F, n):
            dt = 10.0 #time resolution in us
            #convert values
            F = F * convert #to mm/us
            vertprev = 0.0
            horprev = 0.0
            x = 0.0
            y = 0.0
            xprev = 0.0
            yprev = 0.0
            ydirection = 1.0
            xpulwave = []
            ypulwave = []
            xdirwave = []
            ydirwave = []

            totalxpulses = 0
            totalypulses = 0

            #get mm reslution
            #based on maximum speed resolution
            #the mm resolution must be such that the time steps have a velocity < the feed rate
            #First approximation fails in certain cases
            #du = F*dt/(A*2.0*PI/T)/2.0
            #more accurate:
            du = (T / (2.0*PI))*math.asin(F*dt/A)
            print(du)
            curt = 0 #current time
            txprev = 0 #location of previous pulse
            typrev = 0 #location of previous pulse
            tdprev = 0 #location of previous direction pulse

            f = open("log.txt", "w")

            for u in frange(0, T, du):
                #first create a basic sine wave at each point
                vertpos = A * math.sin(2*PI*u/T)
                #get derivatives at each step
                dvert = (vertpos - vertprev) / dt
                vertprev = vertpos
                #find x speed such that the resultant speed is F
                dhor = math.sqrt(F*F - dvert*dvert)
                #get the correct x values
                x = x + dt*dhor
                curt = curt + dt
                y = A * math.sin(2*PI*x/T)
                #generate pulse trains
                if (x - xprev >= mmperstep):
                    xprev = x
                    totalxpulses = 1 + totalxpulses
                    xpulwave.append(pigpio.pulse(0, 1<<GPIOxpul,int(curt-txprev-dt)))
                    f.write(x + "," + curt)
                    xpulwave.append(pigpio.pulse(1<<GPIOxpul, 0, int(dt)))
                    txprev = curt
                #check for changes in direction
                if (y - yprev < 0.0):
                    ydirection = -1.0*ydirection
                    if (ydirection < 0):
                        #have ydir on up until this moment
                        ydirwave.append(pigpio.pulse(1<<GPIOydir, 0, int(curt-tdprev-dt)))
                        tdrev = curt
                    else:
                        #have ydir off up until this moment
                        ydirwave.append(pigpio.pulse(0, 1<<GPIOydir, int(curt-tdprev-dt)))
                        tdprev = curt

                if (ydirection*(y - yprev) >= mmperstep):
                    totalypulses = 1 + totalypulses
                    yprev = y
                    ypulwave.append(pigpio.pulse(0, 1<<GPIOypul, int(curt-typrev-dt)))
                    ypulwave.append(pigpio.pulse(1<<GPIOypul, 0, int(dt)))
                    typrev = curt
            if (F < 0.0):
                xdirwave.append(pigpio.pulse(0, 1<<GPIOxdir, int(dt)*len(ypulwave)))
            else:
                xdirwave.append(pigpio.pulse(1<<GPIOxdir, 0, int(dt)*len(xpulwave)))
            f.close()
            print("Sine wave generated.")

            '''# there is a limit of waveform lengths
            # it is supposed to be 12000
            #waves are then split up
            length = 5000

            print(["Total x pulses:", totalxpulses])
            print(["Total y pulses:", totalypulses])
            print(["Length of pulse train", len(xpulwave)])
            if (len(xpulwave) > length):
                for k in range(int(n)):
                    N = int(math.floor(float(len(xpulwave))/ float(length)))
                    for i in range(0, N-1):
                        #print(["Adding subwave:", i])
                        #print(["Start:", i*length])
                        #print(["End:", (i+1)*length - 1])
                        xpwave = xpulwave[i*length:(i+1)*length-1]
                        ypwave = ypulwave[i*length:(i+1)*length-1]
                        xdwave = xdirwave[i*length:(i+1)*length-1]
                        ydwave = ydirwave[i*length:(i+1)*length-1]
                        self.waves.append([xpwave, ypwave, xdwave, ydwave, 1])
                    #add remaining waves
                    if (len(xpulwave) != (N+1)*length):
                        xpwave = xpulwave[(N+1)*length:]
                        ypwave = ypulwave[(N+1)*length:]
                        xdwave = xdirwave[(N+1)*length:]
                        ydwave = ydirwave[(N+1)*length:]
                    self.waves.append([xpwave, ypwave, xdwave, ydwave, 1])
            else:'''
            self.waves.append([xpulwave, ypulwave, xdirwave, ydirwave, n])




            


       #get integer from gcoude commaends
        def toNum(self, mystr):
            return float(mystr.strip(string.ascii_letters))

if __name__ == "__main__":
    waves = Waves()
    waves.addgc("G1 X5 Y5 F100")

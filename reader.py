"""
Contains functions to analyse the wav file, and compute acoustic values
"""

import scipy.io.wavfile as wavfile
import numpy as np
import pylab as pl
from record import *
import creator
import winsound,sys
from scipy.optimize import curve_fit
import threading
from time import sleep

def read(inputfile,ambientfile=None):
    """
    Reads wav file
    """
    rate, data = wavfile.read(inputfile)
    THRESHOLD=1
    if(ambientfile!=None):
        #Correct amplitude offset using ambient.wav
        ambdata = wavfile.read(ambientfile)[1]
        amboffset=int(np.mean(ambdata))
        for x in range(len(data)):
            data[x]-=amboffset
        #Find ambient max threshold of ambient noise
        maxthresh=0
        for x in range(len(ambdata)):
            ambdata[x]-=amboffset
            if ambdata[x]>maxthresh:
                maxthresh=ambdata[x]
        THRESHOLD=int(maxthresh*125/100) #scale by 100%
        T2=maxthresh*15
    #Trim beginning
    for x in range(len(data)):
        if data[x]>T2:
            data=data[x:]
            print "breaking"
            break        
    #Trim end
    continuity=0
    maxcontinuousblocks=int(rate/10)
    for x in range(len(data)):
        if data[x]<=THRESHOLD:
            continuity+=1
            if continuity>=maxcontinuousblocks:
                data=data[:x]
                break
        else:
            continuity=0         
    return data

def f(x,a,b):
    #if x.any()==0: return 650000
    return (a/x)+b

def plotTime(data,rate):
    """
    Plot time domain graph
    """
    t = np.arange(len(data))*1.0/rate
    
    #Plot time domain
    pl.plot(t, data)
    pl.ylabel("Amplitude")
    pl.xlabel("Time(s)")
    pl.show()
    
##def plotFreq(data):
##    """
##    Plot frequency domain graph
##    """
##    p = 20*np.log10(np.abs(np.fft.rfft(data[:2048])))
##    p = np.abs(np.fft.rfft(data[:2048]))
##    f = np.linspace(0, rate/2.0, len(p))
##    pl.plot(f, p)
##    pl.xlabel("Frequency(Hz)")
##    pl.ylabel("Power(dB)")
##    pl.show()

def dB(data,rate):
    """
    Calculate dBu values by performing RMS
    """
    WINDOW=40.0
    i=0

    data2=[]
    while i<WINDOW+1:
        data2.append(1)
        i+=1
    while i+WINDOW<len(data):
##        t=0
##        for val in data[i-WINDOW:i+WINDOW]:
##            t+=(val**2)/len(data[i-WINDOW:i+WINDOW])
        data2.append(20*np.log10(np.sqrt(np.mean(np.abs([s**2 for s in data[i-WINDOW:i+WINDOW]])))))
        i+=1
    
    maxDb=20*np.log10(2**16) #2^16 is the max amplitude in a 16 bit wav file
    data2=-(maxDb-data2)

    return data2


def medianfilter(DAT,WIND=11):
    DAT2=[]
    for i in DAT[:WIND]:
        DAT2.append(i)
    if WIND>=len(DAT):
        return DAT2
    for i in range(WIND,len(DAT)-WIND+1):
        DAT2.append(np.median(DAT[i:i+WIND]))
    for i in DAT[len(DAT)-WIND+1:]:
        DAT2.append(i)
    return DAT2


def medianfilter2(DAT,start,WIND=11):
    TEMP=[]
    for i in DAT:
        TEMP.append(i)
    DAT=DAT[start:]
    DAT2=[]
    for i in DAT[:WIND]:
        DAT2.append(i)
    if WIND>=len(DAT):
        return DAT2
    for i in range(WIND,len(DAT)-WIND+1):
        DAT2.append(np.median(DAT[i:i+WIND]))
    for i in DAT[len(DAT)-WIND+1:]:
        DAT2.append(i)
    return TEMP[:start]+DAT2

def RT(data2,rate,tone_dur,to_plot=False):
    START=-20*np.log10(2**16)
    firstVal=0#int(tone_dur*rate/1000)

    #Find peak
    for x in range(int((tone_dur)*rate*0.9/1000),len(data2)):
        if data2[x]>=START:
            START=data2[x]
            firstVal=x
    
    t2=np.arange(len(data2))*1.0/rate
    t_beg=None
    START -=0.5
    END=START-20
    t_i=0
    
    for x in range(firstVal,len(t2)):
        if data2[x]<=START:
            t_beg=t2[x]
            t_i=x
            break
    count=0
    wind=1
    td=data2[t_i:]
    t_f=None
    CRANGE=300
    while count<=15:
        td=medianfilter(td,wind)
        t_end=None
        t_f=None
        for x in range(t_i,len(t2)):
            if t_end==None and td[x-t_i]<=END:
                t_end=t2[x]
                t_f=x
                break
        sign=1
        extrem=0
      #  print t_i, t_f, t_end
        if(td[t_f-CRANGE+1-t_i]-td[t_f-CRANGE-t_i]>=0):
            sign=1
        else:
            sign=-1
        for i in range(t_f-CRANGE-t_i,min(t_f+CRANGE-t_i,len(t2)-t_i-1)):
            if((td[i+1]-td[i])*sign<0):
                sign*=-1
                extrem+=1
       # print extrem
        if(extrem>=5):
            wind+=2
            count+=1
            continue
        break
##    t = np.arange(len(data2))*1.0/rate
##    popt,pcov=curve_fit(f,t[t_i:t_f],data2[t_i:t_f])
##    print "NEW"
##    tA= popt[0]/((START+40)-popt[1])
##    tB= popt[0]/((START-20)-popt[1])
##    print tA,tB
##    rt=tB-tA
    rt=(t_end-t_beg)*3
    ##print rt
##    dpl=[]
##    for time in t[t_i:]:
##        dpl.append(f(time,popt[0],popt[1]))
##    pl.show()
    if to_plot:
        pl.plot(t2[:t_f+CRANGE],data2[:t_f+CRANGE])
        pl.plot(t[t_i:t_i+len(td)],td,color='g')
        pl.plot(t[t_i:],dpl,color='r')
        pl.ylabel("dBu RMS")
        pl.xlabel("Time(s)")
        pl.axvline(tone_dur/1000., color='k')
        pl.axvline(t_beg, color='r')
        pl.axvline(t_end, color='r')
        pl.show()
        return rt
    else:
        return rt,t_beg,t_end
    
class Play(threading.Thread):
    def run(self):
        sleep(0.5)
        winsound.PlaySound(TONE_FILENAME ,winsound.SND_FILENAME)

RECORDING_FILENAME='rec.wav'
RECORDING_DURATION=1.5
RATE=4410.0

FREQUENCY=1000
TIME=1000
TONE_FILENAME='output.wav'
AMPLITUDE=32760.0
TONE_FRATE=4410.0

class Record(threading.Thread):
    def run(self):
        record(RECORDING_FILENAME,RECORDING_DURATION,RATE)

def c80(data,rate,tone_dur):
    """
    Return C80 value, which is an index of clarity
    """
    t_start=int(tone_dur*rate/1000.)
    t_div=int(80*rate/1000.)+t_start
    early_snd=np.sum(data[t_start:t_div]**2)
    late_snd=np.sum(data[t_div:]**2)
    c80=10*np.log10(float(early_snd)/late_snd)
    return c80

def soundEnergy(data,rate,tone_dur):
    """
    Return total sound energy received
    """
    t_start=int(tone_dur*rate/1000.)
    return np.sum(data[t_start:]**2)


##creator.make_soundfile(FREQUENCY,TIME,TONE_FILENAME,AMPLITUDE,TONE_FRATE)
##
##RATE=4410.0
##data=[]
##t1=Record()
##t2=Play()
##t2.start()
##t1.start()
##while t1.isAlive() or t2.isAlive():
##    continue
##data=read('rec.wav','ambient.wav')
##print "done"
####plotTime(data,RATE)
##data2=[]
##m=10000000
##data2=(dB(data,RATE))
##if(len(data2)<m):
##    m=len(data2)
##data2=data2[:m]
##data=data[:m]
##t = np.arange(m)*1.0/RATE
##pl.plot(t, data,color='g')
##pl.ylabel("Amplitude")
##pl.xlabel("Time(s)")
##pl.show()

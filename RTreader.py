"""
Contains functions to analyse the wav file, and compute acoustic values
"""

import scipy.io.wavfile as wavfile
import numpy as np
import pylab as pl

def read(inputfile,ambientfile=None):
    """
    Reads a wav file,
    corrects mic ambient offset,
    trims everything except first chunk of sound,
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
        for x in range(len(data)):
            ambdata[x]-=amboffset
            if ambdata[x]>maxthresh:
                maxthresh=ambdata[x]
                
        THRESHOLD=int(maxthresh*125/100) #scale by 25%


    #Trim beginning
    for x in range(len(data)):
        if data[x]>THRESHOLD:
            data=data[x:]
            break

    return data
        
##    #Trim end
##    continuity=0
##    maxcontinuousblocks=int(rate/20)
##    for x in range(len(data)):
##        if data[x]<=THRESHOLD:
##            continuity+=1
##            if continuity>=maxcontinuousblocks:
##                data=data[:x]
##                break
##        else:
##            continuity=0

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
    
def plotFreq(data):
    """
    Plot frequency domain graph
    """
    p = 20*np.log10(np.abs(np.fft.rfft(data[:2048])))
    p = np.abs(np.fft.rfft(data[:2048]))
    f = np.linspace(0, rate/2.0, len(p))
    pl.plot(f, p)
    pl.xlabel("Frequency(Hz)")
    pl.ylabel("Power(dB)")
    pl.show()

def dB(data,rate):
    """
    Calculate dBu values by performing RMS
    """
    WINDOW=50.0
    i=0
    
    data2=[]
    while i<WINDOW+1:
        data2.append(1)
        i+=1
    while i+WINDOW<len(data):
        data2.append(np.sqrt(np.mean(np.abs(data[i-WINDOW:i+WINDOW]**2))))
        i+=1
        
    data2=20*np.log10(data2)
    maxDb=20*np.log10(2**16) #2^16 is the max amplitude in a 16 bit wav file
    data2=-(maxDb-data2)

    return data2


def RT(data2,rate,tone_dur,to_plot=True):
    """
    Return Reverbration Time (RT) value
    Plot dB-time graph if to_plot=True, showing the reverbration beginning and end lines
    """
    WINDOW=50.0 #RMS window size

    t2=np.arange(len(data2))*1.0/rate
    START=-20*np.log10(2**16)
    firstVal=0#int(tone_dur*rate/1000)

    #Find peak
    for x in range(int(tone_dur*rate/1000),int((tone_dur+50)*rate/1000)):
        if data2[x]>=START:
            START=data2[x]
            firstVal=x
            
    t_beg=None
    t_end=None

    START -=2
    
    END=START-20
    
    for x in range(firstVal,len(t2)):
        if t_beg==None and data2[x]<=START:
            t_beg=t2[x]
        if t_end==None and data2[x]<=END:
            t_end=t2[x]
            break

    if to_plot:
        pl.plot(t2,data2)
        pl.ylabel("dBu RMS")
        pl.xlabel("Time(s)")
        pl.axvline(tone_dur/1000., color='k')
        pl.axvline(t_beg, color='r')
        pl.axvline(t_end, color='r')
        pl.show()

    #Calculate and return RT using RT20
    rt20=t_end-t_beg
    rt=rt20*3
    return rt

def c80(data,rate,tone_dur):
    """
    Return C80 value, which is an index of clarity
    """
    t_start=int(tone_dur*rate/1000.)
    t_div=int(80*rate/1000.)+t_starat
    early_snd=np.sum(data[t_start:t_div]**2)
    print early_snd

    

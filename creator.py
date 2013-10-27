"""
Create tone of desired frequency, time duration and amplitude

"""

import math
import wave
import struct
 
def make_soundfile(freq=440, ms=1000, fname="test.wav",amp=100.0,frate = 44100.0):
    data_size=int(frate*ms/1000)
    
    sine_list=[]
##    for x in range(data_size/2): #'Pads' the beginning of the file, accounting for the short delay it takes to start recording
##        sine_list.append(0)
    for x in range(data_size):
        sine_list.append(math.sin(2*math.pi*freq*(x/frate)))
     
    wav_file = wave.open(fname, "w")
    
    nchannels = 1
    sampwidth = 2
    framerate = int(frate)
    nframes = data_size
    comptype = "NONE"
    compname = "not compressed"
    wav_file.setparams((nchannels, sampwidth, framerate, nframes,comptype, compname))
    
    for s in sine_list:
        wav_file.writeframes(struct.pack('h', int(s*amp)))
    wav_file.close()
    print( "%s written" % fname )
 
 
# call function
##freq = 5000
##ms=100
##fname = "output.wav"
##amp=5000.0
##frate = 44100.0
## 
##make_soundfile(freq, ms, fname,amp,frate)

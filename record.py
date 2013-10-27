"""
record() records Audio from mic and saves to wav file

"""

import pyaudio
import wave
import sys

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

def record(outputfile,recordtime,frate):
    p = pyaudio.PyAudio()
    RATE=int(frate)

    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = chunk)

    print "* recording"
    all = []
    for i in range(0, int(RATE / chunk * recordtime)):
        data = stream.read(chunk)
        all.append(data)
    #print all[:256]
    print "* done recording"

    stream.close()
    p.terminate()


    # write data to WAVE file
    data = ''.join(all)
    wf = wave.open(outputfile, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

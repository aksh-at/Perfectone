import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi, sqrt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import Tkinter as Tk
import winsound, sys
import record, reader, creator
import scipy.io.wavfile as wavfile
import threading
from time import sleep

#Attributes for the tone to be played
FREQUENCY=1000
TIME=300
TONE_FILENAME='output.wav'
AMPLITUDE=5000.0
TONE_FRATE=44100.0

#Attributes for recording
AMBIENT_FILENAME='ambient.wav'
RECORDING_FILENAME='rec.wav'
RECORDING_DURATION=2
RATE=44100.0


root=Tk.Tk()
root.wm_title("Perfectone")

lastcanvas=None
lastcanvas2=None
lastcanvas3=None


length_label=None
length_entry=None
breadth_label=None
breadth_entry=None
b_button=None

points=[]
values=None
final=[]

creator.make_soundfile(FREQUENCY,TIME,TONE_FILENAME,AMPLITUDE,TONE_FRATE)

length=Tk.IntVar()
breadth=Tk.IntVar()
LENGTH=0
BREADTH=0

mic_x=0
mic_y=0

c80_label=Tk.Label(master=root,text="C80 value will appear here")
RT_label=Tk.Label(master=root,text="RT value will appear here")
SS_label=Tk.Label(master=root,text="Sound Strength value will appear here")
err_label=Tk.Label(master=root,text="")

class Play(threading.Thread):
    def run(self):
        sleep(0.5)
        winsound.PlaySound(TONE_FILENAME ,winsound.SND_FILENAME)

class Record(threading.Thread):
    def run(self):
        record.record(RECORDING_FILENAME,RECORDING_DURATION,RATE)

def compare(values1, values2):
    rt_1,c80_1,ss_1=values1
    rt_2,c80_2,ss_2=values2

    if rt_1>=rt_2+0.05:
        return 1
    elif rt_2>=rt_1+0.05:
        return -1
    
    if c80_1>=c80_2+1:
        return 1
    elif c80_2>=c80_1+1:
        return -1

    if ss_1>=ss_2:
        return 1
    else:
        return -1

def sort(array):
    for j in range(1,len(array)):
        cur=array[j]
        i=j
        while i>0:
            if compare(cur[1],array[i-1][1])>0:
                array[i]=cur
                break
            else:
                array[i]=array[i-1]
                i-=1
        if i==0:
            array[0]=cur
    return array

def getPoints(length, breadth, n):
    i=int(sqrt(n))
    if n%i!=0:
        i-=1
    l=float(i)
    b=float(n/i)

    points=[]

    for i in range(1,int(l+1)):
        for j in range(1,int(b+1)):
            points.append(((i*length/(2*l+1)),(j*breadth/(b+2))))

    return points

def AmbientRecorder():
    global lastcanvas
    
    record.record(AMBIENT_FILENAME,1,RATE)
    data=wavfile.read(AMBIENT_FILENAME) [1]
    t = arange(len(data))*1.0/RATE
    f=Figure(figsize=(4,3),dpi=100)
    a=f.add_subplot(111)

    a.plot(t,data)
    a.set_title('Ambient recording')
    a.set_xlabel('Time')
    a.set_ylabel('Amplitude')

    #canvas.delete(Tk.ALL)
    canvas=FigureCanvasTkAgg(f,master=root)
    canvas.show()

    if lastcanvas!=None:
        lastcanvas.pack_forget()
    lastcanvas=canvas.get_tk_widget()
    lastcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    #canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    label.config(text="Please check the waveform for any unwanted noises. Record again?")

def ValueEntry():
    global lastcanvas,length_label,length_entry,breadth_label,breadth_entry,b_button
    if lastcanvas!=None:
        lastcanvas.pack_forget()
        lastcanvas=None
        
    label.config(text="Please enter the dimensions of your room")
    y_button.pack_forget()
    n_button.pack_forget()
    
    length_label=Tk.Label(master=root,text="Length (feet): ")
    length_entry=Tk.Entry(master=root,textvariable=length)
    breadth_label=Tk.Label(master=root,text="Breadth(feet): ")
    breadth_entry=Tk.Entry(master=root,textvariable=breadth)
    b_button = Tk.Button(master=root, text='Begin', command=Validate)

    err_label.pack()
    length_label.pack(side=Tk.TOP)
    length_entry.pack(side=Tk.TOP)
    breadth_label.pack(side=Tk.TOP)
    breadth_entry.pack(side=Tk.TOP)
    b_button.pack(side=Tk.TOP)

def Validate():
    global LENGTH, BREADTH
    try:
        LENGTH=int(length.get())
        BREADTH=int(breadth.get())
    except:
        err_label.config(text="Data entry is incorrect. Please enter only numerals")
        return
    if LENGTH<=0 or BREADTH<=0:
        err_label.config(text="Data entry is incorrect. Please enter only numerals")
        return
    else:
        Execute()
    

def Execute():
    global points,mic_x,mic_y

    length_label.pack_forget()
    length_entry.pack_forget()
    breadth_label.pack_forget()
    breadth_entry.pack_forget()
    b_button.pack_forget()

    points=getPoints(LENGTH,BREADTH,4)

    mic_x=LENGTH/2
    mic_y=BREADTH-points[0][1]

    Measure()

def Prepare():
    global final,values
    final.append((points.pop(),values))
    values=None
    
    if len(points)==0:
        Final()
    else:
        Measure()

def Measure():
    global points,lastcanvas,lastcanvas2,lastcanvas3
    
    if lastcanvas!=None:
        lastcanvas.pack_forget()
        lastcanvas=None
    if lastcanvas2!=None:
        lastcanvas2.pack_forget()
        lastcanvas2=None
    if lastcanvas3!=None:
        lastcanvas3.pack_forget()
        lastcanvas3=None
        
    WIDTH=400
    HEIGHT=200

    label.config(text="Please place your speakers at the given points in your room. Press BEGIN to measure attributes")

    

    c80_label.config(text="C80 value will appear here")
    RT_label.config(text="RT value will appear here")
    SS_label.config(text="Sound Strength value will appear here")
    
    c80_label.pack()
    RT_label.pack()
    SS_label.pack()
        
    y_button.config(text="Begin", command=ToneBurst)
    y_button.pack(side=Tk.TOP)
    
    n_button.config(command=ToneBurst,state=Tk.DISABLED)
    n_button.pack(side=Tk.TOP)
        
    lastcanvas3=Tk.Canvas(master=root, width=WIDTH, height=HEIGHT)
    lastcanvas3.pack()

    cds=points[-1]

    lastcanvas3.create_rectangle(0, 0, WIDTH, HEIGHT, fill="white")
    
    lastcanvas3.create_line(0, int(cds[1]*HEIGHT/BREADTH), int(cds[0]*WIDTH/LENGTH), int(cds[1]*HEIGHT/BREADTH))
    lastcanvas3.create_line(WIDTH, int(cds[1]*HEIGHT/BREADTH), WIDTH-int(cds[0]*WIDTH/LENGTH), int(cds[1]*HEIGHT/BREADTH))
    
    lastcanvas3.create_line(int(cds[0]*WIDTH/LENGTH), 0, int(cds[0]*WIDTH/LENGTH), int(cds[1]*HEIGHT/BREADTH))
    lastcanvas3.create_line(WIDTH-int(cds[0]*WIDTH/LENGTH), 0, WIDTH-int(cds[0]*WIDTH/LENGTH), int(cds[1]*HEIGHT/BREADTH))
    
    lastcanvas3.create_rectangle(int(cds[0]*WIDTH/LENGTH)+2, int(cds[1]*HEIGHT/BREADTH)+2, int(cds[0]*WIDTH/LENGTH)-3, int(cds[1]*HEIGHT/BREADTH)-3, fill="red")
    lastcanvas3.create_rectangle(WIDTH-int(cds[0]*WIDTH/LENGTH)+2, int(cds[1]*HEIGHT/BREADTH)+2, WIDTH-int(cds[0]*WIDTH/LENGTH)-3, int(cds[1]*HEIGHT/BREADTH)-3, fill="red")
    lastcanvas3.create_rectangle(int(mic_x*WIDTH/LENGTH)+2, int(mic_y*HEIGHT/BREADTH)+2, int(mic_x*WIDTH/LENGTH)-3, int(mic_y*HEIGHT/BREADTH)-3, fill="yellow")

    lastcanvas3.create_text(int(cds[0]*WIDTH/LENGTH)/2,int(cds[1]*HEIGHT/BREADTH)+10,text=str(cds[0])+" feet")
    lastcanvas3.create_text(WIDTH-int(cds[0]*WIDTH/LENGTH)/2,int(cds[1]*HEIGHT/BREADTH)+10,text=str(cds[0])+" feet")
    lastcanvas3.create_text(int(cds[0]*WIDTH/LENGTH)+30,int(cds[1]*HEIGHT/BREADTH)/2,text=str(cds[1])+" feet")
    lastcanvas3.create_text(int(mic_x*WIDTH/LENGTH), int(mic_y*HEIGHT/BREADTH)+10,text="Mic position")

def ToneBurst():
    global points,lastcanvas,lastcanvas2,values
    t1=Record()
    t2=Play()
    t2.start()
    t1.start()
    while t1.isAlive() or t2.isAlive():
        continue

    data=reader.read(RECORDING_FILENAME,AMBIENT_FILENAME)
    t = arange(len(data))*1.0/RATE
    f=Figure(figsize=(6,4),dpi=100)
    a=f.add_subplot(111)

    a.plot(t,data)
    a.set_title('Amplitude Waveform')
    a.set_xlabel('Time')
    a.set_ylabel('Amplitude')

    canvas=FigureCanvasTkAgg(f,master=root)
    canvas.show()
    
    if lastcanvas!=None:
        lastcanvas.pack_forget()
    lastcanvas=canvas.get_tk_widget()
    lastcanvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

    canvas._tkcanvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

    c80=reader.c80(data,RATE,TIME)
    c80_string="Clarity(C80) value is "+str(c80)+" dB"
    c80_label.config(text=c80_string)
    
    snd_energy=reader.soundEnergy(data,RATE,TIME)
    SS_string="Strength of sound received is "+str(snd_energy)
    SS_label.config(text=SS_string)
    
    data2=reader.dB(data,RATE)      
    t2=arange(len(data2))*1.0/RATE
    f2=Figure(figsize=(6,4),dpi=100)
    a2=f2.add_subplot(111)

    a2.plot(t2,data2)
    a2.set_title('Sound Pressue Levels')
    a2.set_xlabel('Time')
    a2.set_ylabel('dBu(RMS)')
    
    try:
        r_time,t_beg,t_end=reader.RT(data2,RATE,TIME,False)
        RT_string="Reverberation Time (RT20) is "+str(r_time*1000)+" milliseconds. \n(Note:The red interval shows 20dB decay, which is extrapolated over 60dB to get RT)"
        RT_label.config(text=RT_string)
        a2.axvline(TIME/1000., color='k')
        a2.axvline(t_beg, color='r')
        a2.axvline(t_end, color='r')
    except:
        RT_string="Reverberation Time could not be measured. Try increasing the volume, or try a Frequency between 250 Hz and 2000 Hz"
        RT_label.config(text=RT_string)
  
    canvas2=FigureCanvasTkAgg(f2,master=root)
    canvas2.show()
    
    if lastcanvas2!=None:
        lastcanvas2.pack_forget()
    lastcanvas2=canvas2.get_tk_widget()
    lastcanvas2.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
    canvas2._tkcanvas.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
    
    values=(r_time,c80,snd_energy)
    
    label.config(text="Please check if all values have been recorded. Measure again?")
    y_button.config(text="Yes")
    n_button.config(command=Prepare,state=Tk.NORMAL)

def Final():
    global final,lastcanvas,lastcanvas2,lastcanvas3
    final=sort(final)
    if lastcanvas!=None:
        lastcanvas.pack_forget()
        lastcanvas=None
    if lastcanvas2!=None:
        lastcanvas2.pack_forget()
        lastcanvas2=None
    if lastcanvas3!=None:
        lastcanvas3.pack_forget()
        lastcanvas3=None
        
    WIDTH=400
    HEIGHT=200

    label.config(text="The following is the best speaker configuration.")
    
    c80_label.config(text="C80 value is greater than the worst configuration by "+str(final[-1][1][1]-final[0][1][1])+" dB")
    RT_label.config(text="RT value is greater than the worst configuration by "+str(final[-1][1][0]-final[0][1][0])+" dB")
    SS_label.config(text="Sound Strength is greater than the worst configuration by"+str(final[-1][1][2]-final[0][1][2])+" dB")
    
    c80_label.pack()
    RT_label.pack()
    SS_label.pack()
        
    y_button.pack_forget()
    n_button.pack_forget()
        
    lastcanvas3=Tk.Canvas(master=root, width=WIDTH, height=HEIGHT)
    lastcanvas3.pack()

    cds=final[-1][0]

    lastcanvas3.create_rectangle(0, 0, WIDTH, HEIGHT, fill="white")
    
    lastcanvas3.create_line(0, int(cds[1]*HEIGHT/BREADTH), int(cds[0]*WIDTH/LENGTH), int(cds[1]*HEIGHT/BREADTH))
    lastcanvas3.create_line(WIDTH, int(cds[1]*HEIGHT/BREADTH), WIDTH-int(cds[0]*WIDTH/LENGTH), int(cds[1]*HEIGHT/BREADTH))
    
    lastcanvas3.create_line(int(cds[0]*WIDTH/LENGTH), 0, int(cds[0]*WIDTH/LENGTH), int(cds[1]*HEIGHT/BREADTH))
    lastcanvas3.create_line(WIDTH-int(cds[0]*WIDTH/LENGTH), 0, WIDTH-int(cds[0]*WIDTH/LENGTH), int(cds[1]*HEIGHT/BREADTH))
    
    lastcanvas3.create_rectangle(int(cds[0]*WIDTH/LENGTH)+2, int(cds[1]*HEIGHT/BREADTH)+2, int(cds[0]*WIDTH/LENGTH)-3, int(cds[1]*HEIGHT/BREADTH)-3, fill="red")
    lastcanvas3.create_rectangle(WIDTH-int(cds[0]*WIDTH/LENGTH)+2, int(cds[1]*HEIGHT/BREADTH)+2, WIDTH-int(cds[0]*WIDTH/LENGTH)-3, int(cds[1]*HEIGHT/BREADTH)-3, fill="red")
    lastcanvas3.create_rectangle(int(mic_x*WIDTH/LENGTH)+2, int(mic_y*HEIGHT/BREADTH)+2, int(mic_x*WIDTH/LENGTH)-3, int(mic_y*HEIGHT/BREADTH)-3, fill="yellow")

    lastcanvas3.create_text(int(cds[0]*WIDTH/LENGTH)/2,int(cds[1]*HEIGHT/BREADTH)+10,text=str(cds[0])+" feet")
    lastcanvas3.create_text(WIDTH-int(cds[0]*WIDTH/LENGTH)/2,int(cds[1]*HEIGHT/BREADTH)+10,text=str(cds[0])+" feet")
    lastcanvas3.create_text(int(cds[0]*WIDTH/LENGTH)+30,int(cds[1]*HEIGHT/BREADTH)/2,text=str(cds[1])+" feet")
    lastcanvas3.create_text(int(mic_x*WIDTH/LENGTH), int(mic_y*HEIGHT/BREADTH)+10,text="Mic position")
    

label = Tk.Label(root, text="Record ambient sound? (Please do this atleast once)")
label.pack()

y_button = Tk.Button(master=root, text='Yes', command=AmbientRecorder)
y_button.pack(side=Tk.LEFT)

n_button = Tk.Button(master=root, text='No', command=ValueEntry)
n_button.pack(side=Tk.RIGHT)

Tk.mainloop()


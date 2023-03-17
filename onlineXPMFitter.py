import tkinter as tk
from tkinter import Canvas
import socket, threading
import time
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import urllib.request
import os
from pathlib import WindowsPath, Path
from lmfit.models import SkewedVoigtModel
from lmfit.models import ExponentialGaussianModel
from lmfit import Model
from lmfit import Minimizer, minimize, fit_report, conf_interval, printfuncs
from scipy import integrate
from scipy.special import erfc
from uncertainties.core import wrap
import sched
import csv

schedule = sched.scheduler(time.time, time.sleep)
schedule_start_time = 0.0
eventList = []
time0 = []
volt0 = []
isfibersave = True
total = 0.0


def startSchedule():
    while len( schedule.queue ) < 63 :
      pass
    schedule.run()
    return

def closeshutter(text,dwell) :
  try:
    (WindowsPath.home() / '.shutterclosed').touch()
  except:
    Path('/tmp/.shutterclosed').touch()
  return

def openshutter(text,dwell) :
  try:
    pathExists = (WindowsPath.home() / '.shutterclosed').exists()
    if pathExists == True:
      (WindowsPath.home() / '.shutterclosed').unlink()
  except:
    pathExists = Path('/tmp/.shutterclosed').exists()
    if pathExists == True:
      Path('/tmp/.shutterclosed').unlink()
  return


class grafit(tk.Frame):
    def updateShutter(self, shutterState):
        if shutterState == True:
            print("shutter is Closed")
        else:
            print("shutter is Opened")
        return

    def captureRaw(self):
        data = ''
        #f = urllib.request.urlopen('http://localhost:5022/?COMMAND=curve?')
        f = urllib.request.urlopen('http://134.79.229.21/?COMMAND=curve?')
        data = f.read().decode()
        print('received ' + data)

        wfm = [float(u) for u in data.split(',')]
        # print(len(wfm))

        # CALLING WFMPRE TO CONVERT WFM TO MS AND VOLTS
        #f2 = urllib.request.urlopen('http://localhost:5022/?COMMAND=wfmpre?')
        f2 = urllib.request.urlopen('http://134.79.229.21/?COMMAND=wfmpre?')
        wfmpre = f2.read().decode()
        # print(wfmpre)

        # EXAMPLE WFMPRE:
        # wfmpre = '1;8;ASC;RP;MSB;500;"Ch1, AC coupling, 2.0E-2 V/div, 4.0E-5 s/div, 500 points, Average mode";Y;8.0E-7;0;-1.2E-4;"s";8.0E-4;0.0E0;-5.4E1;"V"'
        t = [1.0e6 * (float(wfmpre.split(';')[8]) * float(i) + float(wfmpre.split(';')[10])) for i in
             range(0, len(wfm))]
        volt = [1.0e3 * ( (float(dl) - float(wfmpre.split(';')[14])) * float(wfmpre.split(';')[12]) - float(
            wfmpre.split(';')[13]) ) for dl in wfm]

        return zip(t, volt)

    def conditionWVF(self, signalBgd, background):

        return signalBgd - background

    def calcTAU(self, t, volt):
        result = self.wavmodel.fit(wvPlot, self.wavparams, x=t, method='nelder')
        # print('results--->', result.ci_out)

        # result = self.wavmodel.fit(wvPlot[t<150],self.wavparams,x=t[t<150])
        b = result.best_values
        # errors = result.ci_out
        tfine = np.arange(t[0], t[-1] + 0.8, (t[1] - t[0]) / 10.0)

        ci_txt = result.ci_report()

        cat = float(ci_txt.split('\n')[1].split('  ')[4])
        an = float(ci_txt.split('\n')[2].split('  ')[4])

        return

    def plotit(self,  text='' , dwell=0.0 , islaser=False ):
        if islaser : #FIXME: the laser traces shouldn't just be getting ignored
          return
        data = ''
        #f = urllib.request.urlopen('http://localhost:5022/?COMMAND=curve?')
        f = urllib.request.urlopen('http://134.79.229.21/?COMMAND=curve?')
        data = f.read().decode()
        print('received ' + data)

        wfm = [float(u) for u in data.split(',')]
        # print(len(wfm))

        # CALLING WFMPRE TO CONVERT WFM TO MS AND VOLTS
        #f2 = urllib.request.urlopen('http://localhost:5022/?COMMAND=wfmpre?')
        f2 = urllib.request.urlopen('http://134.79.229.21/?COMMAND=wfmpre?')
        wfmpre = f2.read().decode()

        # EXAMPLE WFMPRE:
        # wfmpre = '1;8;ASC;RP;MSB;500;"Ch1, AC coupling, 2.0E-2 V/div, 4.0E-5 s/div, 500 points, Average mode";Y;8.0E-7;0;-1.2E-4;"s";8.0E-4;0.0E0;-5.4E1;"V"'
        t = [1.0e6 * (float(wfmpre.split(';')[8]) * float(i) + float(wfmpre.split(';')[10])) for i in
             range(0, len(wfm))]
        volt = [1.0e3 * (((float(dl) - float(wfmpre.split(';')[14]))) * float(wfmpre.split(';')[12]) - float(
            wfmpre.split(';')[13])) for dl in wfm]

        # if len(self.xar) > 5000:
        #     self.xar.pop(0)
        #     self.yar.pop(0)

        try:
            pathExists = (WindowsPath.home() / '.shutterclosed').exists()
        except:
            pathExists = Path('/tmp/.shutterclosed').exists()
        

        #if  (WindowsPath.home() / '.shutterclosed').exists() == False:
        if pathExists == False:
            self.topHat = np.array(wfm)
            dataToFile = np.zeros(17)

            #timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dataToFile[0] = 10.0
            dataToFile[1] = 81.9
            dataToFile[2] = 1.0
            dataToFile[3] = 2.9
            # Waveform to plot
            print(len(self.topHat), len(self.nontopHat))
            wvPlot = self.topHat - self.nontopHat
            wvPlot = [1.0e3 * (((float(dl) - float(wfmpre.split(';')[14]))) * float(wfmpre.split(';')[12]) - float(wfmpre.split(';')[13])) for dl in wvPlot]
            if self.isStandard :
                wts = np.zeros(len(t))
                for idx,ti in zip(range(0,len(t)),t) :
                  if ( ti > -50.0 and ti < -15.0 ) or ( ti > 25.0 and ti < 65.0 ) or ( ti > 125.0 and ti < 150.0 ) :
                    wts[idx]=1.0
                result = self.wavmodel.fit(wvPlot, self.wavparams, weights = wts, x=t, method='nelder', max_nfev=1000)
                b = result.params
                ci_txt = result.ci_report()
            else :
                wts = np.ones(len(t))
                for idx,ti in zip(range(0,len(t)),t) :
                  if ( ti > -50.0 and ti < -15.0 ) or ( ti > 25.0 and ti < 65.0 ) or ( ti > 125.0 and ti < 150.0 ) :
                    wts[idx]=1.0
                result = self.wavmodel.fit(wvPlot, self.wavparams, weights = wts, x=t)
                #result = self.wavmodel.fit(wvPlot, self.wavparams, x=t)
                b = result.best_values
                ci_txt = result.ci_report()

            # print('results--->', result.ci_out)
            catrow = (ci_txt.split('\n')[1].split(':')[1])
            anrow = (ci_txt.split('\n')[2].split(':')[1])
            offstrow = (ci_txt.split('\n')[3].split(':')[1])
            cat = b['cat']
            an = b['an']
            offst = b['offst']
            cat_ll = cat + np.fromstring(catrow,dtype=float,sep=' ')[2]
            cat_ul = cat + np.fromstring(catrow,dtype=float,sep=' ')[4]
            an_ll = an + np.fromstring(anrow,dtype=float,sep=' ')[2]
            an_ul = an + np.fromstring(anrow,dtype=float,sep=' ')[4]
            #print(ci_txt)

            tfine = np.arange(t[0], t[-1] + 0.8, (t[1] - t[0]) / 10.0)

            #cat=49.98262 
            #an=46.10659
            #offst=43.619015

            # adding data to list that gets printed to file ( columns 5 and 6)
            dataToFile[4] = float(cat)
            dataToFile[5] = float(an)
            dataToFile[6] = float(offst)
            dataToFile[8] = float(0.0) #UV
            dataToFile[9] = float(0.0) #IR
            dataToFile[10] = float(result.chisqr/result.nfree) #reduced chisq
            dataToFile[11] = float(0.0)
            dataToFile[12] = float(0.0)

            self.xar.append((time.time() - self.start_time) / 3600)
            ts = self.xar[-1]*3600.0 + self.start_time
            dataToFile[7] = str( ts + 126144000.0 + 2208988800.0 )
            tau_e = (81.9 - 10.0) / np.log(cat / an)
            print('cat and an', cat, an, offst,tau_e,cat-b['cat'],an-b['an'],offst-b['offst'])
            self.yar.append(tau_e)

            upper_bound = -(81.9 - 10.0) / np.log(an_ul / cat_ll)
            lower_bound = -(81.9 - 10.0) / np.log(an_ll / cat_ul)

            # we are appending the data to the row which will be written to the file
            dataToFile[13] = float(cat_ll) 
            dataToFile[14] = float(cat_ul)
            dataToFile[15] = float(an_ll)
            dataToFile[16] = float(an_ul)

            fh = open(self.savePath, 'a')

            writer = csv.writer(fh)
            writer.writerows([dataToFile])
            fh.close()

            self.el.append(tau_e - lower_bound)
            self.eh.append(upper_bound - tau_e)

            self.plt1.clear()
            self.plt2.clear()

            # PLOTTTING PEAKS:
            # self.plt.subplot(211)
            self.plt2.errorbar(self.xar, self.yar, [self.el, self.eh], markersize=6, fmt='o',mec='r',mfc='None')
            self.plt2.set_title("$e^{-}$ Lifetime vs Time")
            self.plt2.set_ylabel('$\\tau$($\mu$s)')
            self.plt2.set_xlabel('Time (h)')
            self.figure2.tight_layout()
            # PLOTTING WAVEFORM:
            # self.plt.subplot(212)
            self.plt1.plot(t, wvPlot, 'g-')
            tfine = np.arange(t[0], t[-1] + 0.8, (t[1] - t[0]) / 10.0)
             
            if self.isStandard :
                #self.plt1.plot(tfine,
                #               self.wavmodel.eval(x=tfine, an=b['an'], cat=b['cat'], tcrise=b['tcrise'],
                #               tarise=b['tarise'], offst=b['offst'], thold=b['thold'] ), 'r-', label='standard')
                self.plt1.plot(tfine,
                               self.wavmodel.eval(x=tfine, cat=cat, an=an, tcrise=b['tcrise'],
                               tarise=b['tarise'], offst=offst, thold=b['thold'] ), 'r-', label='standard')
            else :
                self.plt1.plot(tfine,
                               self.wavmodel.eval(x=tfine, an=b['an'], cat=b['cat'], cent_c=b['cent_c'], tcrise=b['tcrise'],
                               tarise=b['tarise'], cent_a=b['cent_a'], gam_a=b['gam_a'],
                               gam_c=b['gam_c'], skew_a=b['skew_a'], offst=b['offst']), 'r-', label='proposed: an=42.04 mV')

            self.plt1.set_title("Most recent waveform")
            self.plt1.set_ylabel("MilliVolts")
            self.plt1.set_xlabel(u"Time (\u03bcs)")
            self.figure1.tight_layout()
            self.canvas1.draw_idle()
            self.canvas2.draw_idle()

        else:
            self.nontopHat = np.array(wfm)

        self.ctr += 1

        # here we check if the save file has been defined, if so write to it, if not state that it is not set
        try:
            self.saveFile
            if not self.saveFile.closed:
                print('Writing data to save file')
                #try:
                #    dataToFile
                #    if dataToFile.
                #saveData = str( ','.join( str(i) for i in dataToFile)) + '\n'
                #saveFile.write(saveData)
            else:
                print('Save file has been closed')
        except :
            print('Save file is not set')

    def ud(self) :
        try :
            #print('schedule length',len(schedule.queue))
            if len( schedule.queue ) > 0 :
                ct = int((schedule.queue[0][0] - time.time())*100)
            if len( schedule.queue[0][3] ) > 1 and ct > 0 :
                print(schedule.queue[0][3][0]+str(ct/100)+' sec')
            if len( schedule.queue[0][3] ) == 0 :
                print('Busy...Downloading waveforms...')
        except Exception as exc:
            for event in schedule.queue :
                schedule.cancel(event)
            self.saveFile.close()
            openshutter('',0.0)
            #os._exit(0)
        self.parent.after(1000,self.ud)

    def on_closing(self):
        for event in schedule.queue :
            schedule.cancel(event)
        self.saveFile.close()
        openshutter('',0.0)
        #os._exit(0)

    def fitter_func(self, x, cat, an, tcrise, tarise, offst,thold ):
        global err
        #thold = 395.3
        z = np.array(x)
        x_beg = z[z<10.0]
        x_mid = z[(z>=10.0)*(z<81.9)]
        x_end = z[z>=81.9]
        y_beg = 0.5*cat*erfc(-(x_beg-10.0)/tcrise) - 0.5*an*erfc(-(x_beg-81.9)/tarise)
        y_mid = 0.5*cat*erfc(-(x_mid-10.0)/tcrise)*np.exp(-(x_mid-10.0)/thold) - 0.5*an*erfc(-(x_mid-81.9)/tarise)
        y_end = 0.5*cat*erfc(-(x_end-10.0)/tcrise)*np.exp(-(x_end-10.0)/thold) - 0.5*an*erfc(-(x_end-81.9)/tarise)*np.exp(-(x_end-81.9)/thold)
        y = np.concatenate((y_beg,y_mid,y_end),axis=None)
        y = y + offst
        return y

    def extra_smeared(self, x, cat, an, tcrise, cent_c, gam_c, tarise, cent_a, gam_a, skew_a, offst):
        self.catpars['amplitude'].value = cat
        self.catpars['sigma'].value = tcrise
        self.catpars['center'].value = cent_c
        self.catpars['gamma'].value = gam_c
        # tfine = np.arange(x[-1]-1000.0,x[-1],0.08)
        integrand_c = self.catmodel.eval(self.catpars, x=x)
        integral_c = integrate.cumulative_trapezoid(integrand_c, x)
        integral_c = np.append(integral_c, integral_c[-1])
        y = integral_c * np.exp(-(x - 10.0) / 395.3)
        self.pars['amplitude'].value = an
        self.pars['sigma'].value = tarise
        self.pars['center'].value = cent_a
        self.pars['gamma'].value = gam_a
        self.pars['skew'].value = skew_a
        integrand_a = self.pkmodel.eval(self.pars, x=x)
        integral_a = integrate.cumulative_trapezoid(integrand_a, x)
        integral_a = np.append(integral_a, integral_a[-1])
        y = y - integral_a * np.exp(-(x - 81.9) / 395.3)
        y = y + offst
        return y

    def control(self):
        try :
            global total
            dwellclosed = 32.0
            dwellopen = float(self.waitT_input.get())
            fibersavetime = 300.0 #for fibersave
            tbc = dwellclosed
            tf = 0 
            if len( schedule.queue ) == 0 or ( len(schedule.queue) == 7  and root.graph.ctr > 0 ) : 
                for iii in range(0,10) :
                    iodelay = 12
                    text = '*Initializing acquisition ---SHUTTER CLOSED--- '
                    #print(text)
                    if isfibersave and root.graph.ctr > 0 and iii == 0 : 
                        text = '*Fiber-saving mode: ---SHUTTER CLOSED--- resume in '
                    schedule.enter( total, 1, closeshutter, argument=(text,1.0) )
                    text = '*Acquisition mode ---SHUTTER CLOSED--- capture background trace in '
                    #if isfibersave and root.graph.ctr > 0 :
                    #  text = '*Fiber-saving mode: ---SHUTTER CLOSED--- next acquisition in '
                    total = total + 1 + dwellclosed
                    schedule.enter( total, 1, root.graph.plotit, argument=(text,dwellclosed) )
                    #total = total + iodelay
                    total = total + 1 
                    text = '*Capturing (signal+background) ---OPENING SHUTTER--- '
                    schedule.enter( total, 1, openshutter, argument=(text,1.0) )
                    text = 'Acquisition mode ---SHUTTER OPEN--- capture (signal+background) in '
                    total = total + dwellopen 
                    schedule.enter( total, 1, root.graph.plotit, argument=(text,dwellopen))
                    #text = 'Acquisition mode ---SHUTTER OPEN--- capturing laser traces '
                    total = total + 1 
                    schedule.enter( total, 1, root.graph.plotit , argument = ('Getting UV Laser trace ',1.0,True) )
                    total = total + 1 
                    schedule.enter( total, 1, root.graph.plotit , argument = ('Getting IR Laser trace ',1.0,True) )
                    if isfibersave and iii == 9 : 
                        text = '*Fiber-saving mode: ---CLOSING SHUTTER--- '
                        #print(text)
                        total = total + 1 
                        schedule.enter( total, 1, closeshutter, argument=(text,1.0) )
                        total = total + fibersavetime
                    else :
                        total = total + 1 
                        text = '*Acquisition mode ---CLOSING SHUTTER--- preparing next acquisition '
                        schedule.enter( total, 1, closeshutter, argument=(text,1.0) )
                        total = total + tbc 
                if isfibersave : 
                    total = fibersavetime
                else :
                    total = tbc
        except Exception as exc :
            for event in schedule.queue :
                schedule.cancel(event)
            self.saveFile.close()
            #os._exit(0)
        self.parent.after(10, self.control)

    def set_saveFile(self):
        self.control()    
        def close_saveFile():
            print('File closed')
            saveFile.close()

        self.savePath=self.fileSaveInput.get('1.0', 'end-1c')
        self.currSavePath = tk.Label(height=1, width=30)
        self.currSavePath.config(text="File Path: " + self.savePath)
        self.currSavePath.grid(row=2, column=1)

        # the file that the info will be saved to( open appropriate one when path is specified) 
        self.saveFile = open(r'%s' % (self.savePath), "a")
        #saveFile.write("Hello saveFile\n")

    def __init__(self, parent):
        self.ctr = 0
        self.start_time = time.time()
        self.topHat = []
        self.nontopHat = []
        try:
                self.saveFile = open('/dev/null','r')
        except:
                self.saveFile = open('NUL','r')
        tk.Frame.__init__(self, parent)
        # Set up figure and plot
        #self.figure = Figure(figsize=(3, 5), dpi=100)
        #self.figure = Figure(figsize=(6, 5), dpi=100)

        #self.plt = self.figure.add_subplot(111)

        # Create parent, which is the class onlineXPMFitter from down below
        self.parent = parent
        self.parent.configure(bg="lightgray") # set the background color
        #self.T = tk.Text(self.parent, height=1, width=5, font=("Courier", 64))
        #self.T.grid(row=0, column=1)
        #self.T.config(foreground="blue")
        self.isStandard = True

        if self.isStandard :
          self.p_i = [49.98262, 46.10659, 10.0, 1.0, 2.9, 81.9, 395.3, 0.8, 0.9, 43.619015]
          self.wavmodel = Model(self.fitter_func,nan_policy='raise')
          self.wavparams = self.wavmodel.make_params()
          self.wavparams['cat'].value = self.p_i[0]
          self.wavparams['cat'].vary = True
          self.wavparams['an'].value = self.p_i[1]
          self.wavparams['an'].vary = True
          self.wavparams['thold'].value = self.p_i[6]
          self.wavparams['thold'].vary = False
          self.wavparams['tcrise'].value = self.p_i[3]
          self.wavparams['tcrise'].vary = False
          self.wavparams['tarise'].value = self.p_i[4]
          self.wavparams['tarise'].vary = False
          self.wavparams['offst'].value = self.p_i[9]
          self.wavparams['offst'].vary = True
        else :
          self.p_i = [37.873185672822736, 40.81570955383812, 10.0, 3.598, 0.980325759727434, 81.9, 1.80825, 0.8, 0.9, 0.2]
          self.wavmodel = Model(self.extra_smeared, nan_policy='raise')
          self.wavparams = self.wavmodel.make_params()
          self.wavparams['cat'].value = self.p_i[0]
          self.wavparams['cat'].vary = True
          self.wavparams['an'].value = self.p_i[1]
          self.wavparams['an'].vary = True
          self.wavparams['cent_c'].value = self.p_i[2]
          self.wavparams['cent_c'].vary = False
          # self.wavparams['thold'].value = self.p_i[3]
          # self.wavparams['thold'].vary = False
          self.wavparams['tcrise'].value = self.p_i[3]
          self.wavparams['tcrise'].vary = False
          self.wavparams['tarise'].value = self.p_i[4]
          self.wavparams['tarise'].vary = False
          self.wavparams['cent_a'].value = self.p_i[5]
          self.wavparams['cent_a'].vary = False
          self.wavparams['gam_a'].value = self.p_i[6]
          self.wavparams['gam_a'].vary = False
          self.wavparams['skew_a'].value = self.p_i[7]
          self.wavparams['skew_a'].vary = False
          self.wavparams['gam_c'].value = self.p_i[8]
          self.wavparams['gam_c'].vary = False
          self.wavparams['offst'].value = self.p_i[9]
          self.wavparams['offst'].vary = True
        
        self.pkmodel = SkewedVoigtModel()
        self.catmodel = ExponentialGaussianModel()
        self.pars = self.pkmodel.make_params()
        self.catpars = self.catmodel.make_params()

        self.xar = []
        self.yar = []
        self.el = []
        self.eh = []
	
	# seconds to wait between captures
        self.waitT_label = tk.Label(height=1, width=30)
        self.waitT_label.config(text="Seconds to wait between captures")
        self.waitT_label.grid(row=1, column=1)

        # seconds to wait input
        defaultTime = tk.StringVar(self.parent)
        defaultTime.set('33.0')
        self.waitT_input = tk.Spinbox(self.parent, increment=1.0, foreground='black', background='white', textvariable=defaultTime)
        self.waitT_input.grid(row=4, column=1)

        # next two lines are for the texbox for entries
        self.fileSaveInput = tk.Text( height=1, width=30, bg='gray') # text box( where user enters path)
        self.fileSaveInput.insert(tk.END,'testData')
        self.fileSaveInput.grid( row=3, column=1)

        # button to commit the save path ( technically starts before)
        self.commitLocationButton = tk.Button(text="Start", command=lambda:self.set_saveFile())
        self.commitLocationButton.grid(row=3, column=2)

        # positioning of the graphs
        self.figure1 = Figure(figsize=(4, 4), dpi=100)
        self.figure2 = Figure(figsize=(4, 4), dpi=100)

        self.plt1 = self.figure1.add_subplot(111)
        self.plt2 = self.figure2.add_subplot(111)

        self.canvas1 = FigureCanvasTkAgg(self.figure1, master=self.parent)
        self.canvas2 = FigureCanvasTkAgg(self.figure2, master=self.parent)
        # self.graph = Graph(self)
        # self.canvas = self.graph.canvas
        self.plot_widget1 = self.canvas1.get_tk_widget()
        self.plot_widget2 = self.canvas2.get_tk_widget()

        self.plot_widget1.grid(row=1, column=5)
        self.plot_widget2.grid(row=1, column=6)

        # self.fig.canvas.draw()

        # self.plotter = threading.Thread(target=self.plotit)
        # self.plotter.setDaemon(True) # MAKES CODE THREAD SAFE

    def increment(self):
        self.value.set(self.value.get() + 1)

    def decrement(self):
        self.value.set(self.value.get() - 1)

    def filter_key(self, event):
        if not event.char.isdigit() and event.keysym not in ('BackSpace', 'Delete'):
            return 'break'



class onlineXPMFitter(tk.Tk):
    """ Class instance of main/root window. Mainly responsible for showing the
        core components and setting other properties related to the main window."""

    def __init__(self):
        tk.Tk.__init__(self)

        # Set title and screen resolutions
        tk.Tk.wm_title(self, 'XPM Fitter')
        tk.Tk.minsize(self, width=840, height=520)
        # Optional TODO: Set a custom icon for the XPM application
        # tk.Tk.iconbitmap(self, default="[example].ico")

        # Show window and control bar
        self.graph = grafit(self)
        # self.graph.pack(side='top', fill='both', expand=True)

root = onlineXPMFitter()

scheduThread = threading.Thread(target=startSchedule)
schedule_start_time = time.time()
root.graph.ud()
time.sleep(1.0)
#scheduThread.setDaemon(True)
scheduThread.setDaemon(True)
scheduThread.start()
root.mainloop()

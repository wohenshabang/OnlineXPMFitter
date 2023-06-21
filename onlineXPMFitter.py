import tkinter as tk
import socket, threading
import time
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import urllib.request
import os
from lmfit.models import SkewedVoigtModel
from lmfit.models import ExponentialGaussianModel
from lmfit import Model
from scipy import integrate
from scipy.special import erfc
from uncertainties.core import wrap
import sched

schedule = sched.scheduler(time.time, time.sleep)
eventList = []


class grafit(tk.Frame):
    def updateShutter(self, shutterState):
        if shutterState == True:
            print("shutter is Closed")
        else:
            print("shutter is Opened")
        return

    def captureRaw(self):
        data = ''
        f = urllib.request.urlopen('http://localhost:5022/?COMMAND=curve?')
        # f = urllib.request.urlopen('http://134.79.229.21/?COMMAND=curve?')
        data = f.read().decode()
        print('received ' + data)

        wfm = [float(u) for u in data.split(',')]
        # print(len(wfm))

        # CALLING WFMPRE TO CONVERT WFM TO MS AND VOLTS
        f2 = urllib.request.urlopen('http://localhost:5022/?COMMAND=wfmpre?')
        # f2 = urllib.request.urlopen('http://134.79.229.21/?COMMAND=wfmpre?')
        wfmpre = f2.read().decode()
        # print(wfmpre)

        # EXAMPLE WFMPRE:
        # wfmpre = '1;8;ASC;RP;MSB;500;"Ch1, AC coupling, 2.0E-2 V/div, 4.0E-5 s/div, 500 points, Average mode";Y;8.0E-7;0;-1.2E-4;"s";8.0E-4;0.0E0;-5.4E1;"V"'
        t = [1.0e6 * (float(wfmpre.split(';')[8]) * float(i) + float(wfmpre.split(';')[10])) for i in
             range(0, len(wfm))]
        volt = [1.0e3 * (((dl / 256) - float(wfmpre.split(';')[14])) * float(wfmpre.split(';')[12]) - float(
            wfmpre.split(';')[13])) for dl in wfm]

        return zip(t, volt)

    def conditionWVF(self, signalBgd, background):

        return signalBgd - background

    def calcTAU(self, t, volt):
        result = self.wavmodel.fit(wvPlot, self.wavparams, x=t)
        # print('results--->', result.ci_out)

        # result = self.wavmodel.fit(wvPlot[t<150],self.wavparams,x=t[t<150])
        b = result.best_values
        # errors = result.ci_out
        tfine = np.arange(t[0], t[-1] + 0.8, (t[1] - t[0]) / 10.0)

        ci_txt = result.ci_report()

        cat = float(ci_txt.split('\n')[1].split('  ')[4])
        an = float(ci_txt.split('\n')[2].split('  ')[4])

        return

    def plotit(self):

        data = ''
        f = urllib.request.urlopen('http://localhost:5022/?COMMAND=curve?')
        # f = urllib.request.urlopen('http://134.79.229.21/?COMMAND=curve?')
        data = f.read().decode()
        print('received ' + data)



        # here we check if the save file has been defined, if so write to it, if not state that it is not set
        try:
            saveFile
            if not saveFile.closed:
                print('Writing data to save file')
                saveFile.write(data)
            else:
                print('Save file has been closed')
        except NameError:
            print('Save file is not set')



        wfm = [float(u) for u in data.split(',')]
        # print(len(wfm))

        # CALLING WFMPRE TO CONVERT WFM TO MS AND VOLTS
        f2 = urllib.request.urlopen('http://localhost:5022/?COMMAND=wfmpre?')
        # f2 = urllib.request.urlopen('http://134.79.229.21/?COMMAND=wfmpre?')
        wfmpre = f2.read().decode()
        # print(wfmpre)

        # EXAMPLE WFMPRE:
        # wfmpre = '1;8;ASC;RP;MSB;500;"Ch1, AC coupling, 2.0E-2 V/div, 4.0E-5 s/div, 500 points, Average mode";Y;8.0E-7;0;-1.2E-4;"s";8.0E-4;0.0E0;-5.4E1;"V"'
        t = [1.0e6 * (float(wfmpre.split(';')[8]) * float(i) + float(wfmpre.split(';')[10])) for i in
             range(0, len(wfm))]
        volt = [1.0e3 * (((dl / 256) - float(wfmpre.split(';')[14])) * float(wfmpre.split(';')[12]) - float(
            wfmpre.split(';')[13])) for dl in wfm]

        if self.ctr % 2 == 1:
            self.topHat = np.array(volt)
        else:
            self.nontopHat = np.array(volt)

        # print(f"t: {len(t)}")
        # print(f"volt: {len(volt)}")

        # FINDING PEAK / UPSTROKE SIZE:

        # begin search for start of upstroke after 50us:
        # fiftymus = np.argmax( np.array(t) > 50.0 )
        # print("fiftymus: " , fiftymus)
        # volt_subset = volt[:fiftymus]
        # max_index = np.argmax(volt_subset) # give all elements of array greater than 50
        # print("max index: ", max_index)
        # # search for minimum either 50 points back or less in the subset:
        # start = max_index - 50
        # print("start: ", start)
        # if start < 0 : start = 0
        # try :
        #     peak = volt_subset[max_index] - np.min( np.array(volt_subset)[start:max_index] )
        # except ValueError:
        #     print('max_index',str(max_index))
        #     print(volt_subset)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # if len(self.xar) > 5000:
        #     self.xar.pop(0)
        #     self.yar.pop(0)

        # plot if there is an odd iteration of whhile loop
        if self.ctr % 2 == 1:
            # Waveform to plot
            print(len(self.topHat), len(self.nontopHat))
            wvPlot = self.topHat - self.nontopHat
            result = self.wavmodel.fit(wvPlot, self.wavparams, x=t)
            # print('results--->', result.ci_out)

            # result = self.wavmodel.fit(wvPlot[t<150],self.wavparams,x=t[t<150])
            b = result.best_values
            # errors = result.ci_out
            tfine = np.arange(t[0], t[-1] + 0.8, (t[1] - t[0]) / 10.0)

            ci_txt = result.ci_report()

            cat = float(ci_txt.split('\n')[1].split('  ')[4])
            an = float(ci_txt.split('\n')[2].split('  ')[4])

            print('cat and an', cat, an)

            self.xar.append((time.time() - self.start_time) / 3600)
            self.yar.append((81.9 - 10.0) / np.log(cat / an))

            # yvar = (81.9-10.0)/np.log(result.ci_out['cat'][3][1]/result.ci_out['an'][3][1])
            # upper_bound = (81.9-10.0)/np.log((result.ci_out['cat'][2][1]/result.ci_out['an'][4][1]))
            # lower_bound = (81.9-10.0)/np.log((result.ci_out['cat'][4][1]/result.ci_out['an'][2][1]))
            # # print(yvar,lower_bound,upper_bound)

            cat_ll = float(ci_txt.split('\n')[1].split('  ')[4]) + float(ci_txt.split('\n')[1].split('  ')[5])
            cat_ul = float(ci_txt.split('\n')[1].split('  ')[6]) + float(ci_txt.split('\n')[1].split('  ')[5])
            an_ll = float(ci_txt.split('\n')[2].split('  ')[4]) + float(ci_txt.split('\n')[2].split('  ')[5])
            an_ul = float(ci_txt.split('\n')[2].split('  ')[6]) + float(ci_txt.split('\n')[2].split('  ')[5])
            upper_bound = -(81.9 - 10.0) / np.log(an_ul / cat_ll)
            lower_bound = -(81.9 - 10.0) / np.log(an_ll / cat_ul)

            # self.yar.append(yvar)

            self.el.append(lower_bound)
            self.eh.append(upper_bound)
            # # errormatrix = np.array( [self.el, self.eh])

            # self.plt1.plot(tfine,self.wavmodel.eval(x=tfine,an=b['an'],cat=b['cat'],cent_c=b['cent_c'],tcrise=b['tcrise'],tarise=b['tarise'],cent_a=b['cent_a'],gam_a=b['gam_a'],gam_c=b['gam_c'],skew_a=b['skew_a'],offst=b['offst']),'r-',label='proposed: an=42.04 mV')

            self.plt1.clear()
            self.plt2.clear()

            # PLOTTTING PEAKS:
            # self.plt.subplot(211)
            self.plt2.errorbar(self.xar, self.yar, [self.el, self.eh], markersize=6, fmt='ro')
            self.plt2.set_title("$e^{-}$ Lifetime vs Time")
            self.plt2.set_ylabel('$\\tau$($\mu$s)')
            self.plt2.set_yticklabels(['{:1.1e}'.format(x) for x in self.plt2.get_yticks()])
            self.plt2.set_xlabel('Time (h)')
            # self.plt2.set_ylim(0.0,2.0e4)
            # self.plt2.tick_params(axis='both',which='major',labelsize=9)
            # self.plt2.tick_params(axis='both',which='minor',labelsize=9)
            # self.figure1.tight_layout()
            self.figure2.tight_layout()
            # PLOTTING WAVEFORM:
            # self.plt.subplot(212)
            self.plt1.plot(t, wvPlot, 'go-')
            tfine = np.arange(t[0], t[-1] + 0.8, (t[1] - t[0]) / 10.0)
            self.plt1.plot(tfine,
                           self.wavmodel.eval(x=tfine, an=b['an'], cat=b['cat'], cent_c=b['cent_c'], tcrise=b['tcrise'],
                                              tarise=b['tarise'], cent_a=b['cent_a'], gam_a=b['gam_a'],
                                              gam_c=b['gam_c'], skew_a=b['skew_a'], offst=b['offst']), 'r-',
                           label='proposed: an=42.04 mV')

            self.plt1.set_title("Most recent waveform")
            self.plt1.set_ylabel("MilliVolts")
            self.plt1.set_xlabel(u"Time (\u03bcs)")

            # self.plt.subplots_adjust(hspace=0.6, wspace=0.6)
            # self.plot_widget.grid(row=0, column=0, rowspan=2)

            # WIDGET TO SEE MOST RECENT PEAK

            # peak = round(peak, 1)
            # self.T.insert(tk.END, peak)

            self.canvas1.draw_idle()
            self.canvas2.draw_idle()
        # originally 5:
        # time.sleep(1.0)
        self.ctr += 1

        # print('Value of exc',exc)
        # os._exit(0)
        print('Getting here---> plotit')
        self.parent.after(1000, self.plotit)

    '''
    def plotit(self):

        # print(f"t: {len(t)}")
        # print(f"volt: {len(volt)}")

        # FINDING PEAK / UPSTROKE SIZE:

        # begin search for start of upstroke after 50us:
        # fiftymus = np.argmax( np.array(t) > 50.0 )
        # print("fiftymus: " , fiftymus)
        # volt_subset = volt[:fiftymus]
        # max_index = np.argmax(volt_subset) # give all elements of array greater than 50
        # print("max index: ", max_index)
        # # search for minimum either 50 points back or less in the subset:
        # start = max_index - 50
        # print("start: ", start)
        # if start < 0 : start = 0
        # try :
        #     peak = volt_subset[max_index] - np.min( np.array(volt_subset)[start:max_index] )
        # except ValueError:
        #     print('max_index',str(max_index))
        #     print(volt_subset)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # if len(self.xar) > 5000:
        #     self.xar.pop(0)
        #     self.yar.pop(0)

        # plot if there is an odd iteration of whhile loop
        if self.ctr % 2 == 1:
            # Waveform to plot
            print(len(self.topHat), len(self.nontopHat))
            wvPlot = self.topHat - self.nontopHat

            print('cat and an', cat, an)

            self.xar.append((time.time() - self.start_time) / 3600)
            self.yar.append((81.9 - 10.0) / np.log(cat / an))

            # yvar = (81.9-10.0)/np.log(result.ci_out['cat'][3][1]/result.ci_out['an'][3][1])
            # upper_bound = (81.9-10.0)/np.log((result.ci_out['cat'][2][1]/result.ci_out['an'][4][1]))
            # lower_bound = (81.9-10.0)/np.log((result.ci_out['cat'][4][1]/result.ci_out['an'][2][1]))
            # # print(yvar,lower_bound,upper_bound)

            cat_ll = float(ci_txt.split('\n')[1].split('  ')[4]) + float(ci_txt.split('\n')[1].split('  ')[5])
            cat_ul = float(ci_txt.split('\n')[1].split('  ')[6]) + float(ci_txt.split('\n')[1].split('  ')[5])
            an_ll = float(ci_txt.split('\n')[2].split('  ')[4]) + float(ci_txt.split('\n')[2].split('  ')[5])
            an_ul = float(ci_txt.split('\n')[2].split('  ')[6]) + float(ci_txt.split('\n')[2].split('  ')[5])
            upper_bound = -(81.9 - 10.0) / np.log(an_ul / cat_ll)
            lower_bound = -(81.9 - 10.0) / np.log(an_ll / cat_ul)

            # self.yar.append(yvar)

            self.el.append(lower_bound)
            self.eh.append(upper_bound)
            # # errormatrix = np.array( [self.el, self.eh])

            # self.plt1.plot(tfine,self.wavmodel.eval(x=tfine,an=b['an'],cat=b['cat'],cent_c=b['cent_c'],tcrise=b['tcrise'],tarise=b['tarise'],cent_a=b['cent_a'],gam_a=b['gam_a'],gam_c=b['gam_c'],skew_a=b['skew_a'],offst=b['offst']),'r-',label='proposed: an=42.04 mV')

            self.plt1.clear()
            self.plt2.clear()

            # PLOTTTING PEAKS:
            # self.plt.subplot(211)
            self.plt2.errorbar(self.xar, self.yar, [self.el, self.eh], markersize=6, fmt='ro')
            self.plt2.set_title("$e^{-}$ Lifetime vs Time")
            self.plt2.set_ylabel('$\tau$')
            self.plt2.set_xlabel('Time (h)')

            # PLOTTING WAVEFORM:
            # self.plt.subplot(212)
            self.plt1.plot(t, wvPlot, 'go-')
            tfine = np.arange(t[0], t[-1] + 0.8, (t[1] - t[0]) / 10.0)
            self.plt1.plot(tfine,
                           self.wavmodel.eval(x=tfine, an=b['an'], cat=b['cat'], cent_c=b['cent_c'], tcrise=b['tcrise'],
                                              tarise=b['tarise'], cent_a=b['cent_a'], gam_a=b['gam_a'],
                                              gam_c=b['gam_c'], skew_a=b['skew_a'], offst=b['offst']), 'r-',
                           label='proposed: an=42.04 mV')

            self.plt1.set_title("Most recent waveform")
            self.plt1.set_ylabel("MilliVolts")
            self.plt1.set_xlabel(u"Time (\u03bcs)")

            # self.plt.subplots_adjust(hspace=0.6, wspace=0.6)
            # self.plot_widget.grid(row=0, column=0, rowspan=2)

            # WIDGET TO SEE MOST RECENT PEAK

            # peak = round(peak, 1)
            # self.T.insert(tk.END, peak)

            self.canvas1.draw_idle()
            self.canvas2.draw_idle()
        # originally 5:
        # time.sleep(1.0)
        self.ctr += 1

        # print('Value of exc',exc)
        # os._exit(0)
        print('Getting here---> plotit')
        # self.parent.after(1000,self.plotit)
    '''
    def on_closing(self):
        saveFile.close()
        os._exit(0)

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


    def __init__(self, parent):
        self.ctr = 0
        self.start_time = time.time()
        self.topHat = []
        self.nontopHat = []

        # Tk.__init__(self)
        tk.Frame.__init__(self, parent)

        # Set up figure and plot
        #self.figure = Figure(figsize=(3, 5), dpi=100)
        self.figure = Figure(figsize=(6, 5), dpi=100)

        #I changed^^^

        self.plt = self.figure.add_subplot(111)

        # Create parent, which is the class Simulator from down below
        self.parent = parent
        self.T = tk.Text(self.parent, height=1, width=5, font=("Courier", 64))
        self.T.grid(row=0, column=1)
        self.T.config(foreground="blue")

        self.p_i = [37.873185672822736, 40.81570955383812, 10.0, 3.598, 0.980325759727434, 81.9, 1.80825, 0.8, 0.9, 0.2]
        # self.wavmodel = Model(smeared_func,nan_policy='raise')
        self.wavmodel = Model(self.extra_smeared, nan_policy='raise')
        # self.wavmodel = Model(fitter_func,nan_policy='raise')
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
        # self.window = tk.Tk()
        self.el = []
        self.eh = []

        # INITIAL GUI PAGE:
        # self.window.title('Fiber Alignment Tool')
        # self.fig = plt.figure(1)
        # self.fig.text(0.5,0.04,'LOADING...',ha ='center',va = 'center')
        #self.figure1 = Figure(figsize=(3, 5), dpi=100)
        #self.figure2 = Figure(figsize=(3, 5), dpi=100)




        # next two lines are for the texbox for entries
        self.fileSaveInput = tk.Text( height=1, width=30, bg='gray') # text box( where user enters path)
        self.fileSaveInput.grid( row=1, column=1)

        # button to commit the save path
        self.commitLocationButton = tk.Button(text="Commit Path", command=lambda:set_saveFile())
        self.commitLocationButton.grid(row=1, column=2)

        # getting the input save path from user input in textbox
        def set_saveFile():
        
            def close_saveFile():
                print('File closed')
                saveFile.close()

            savePath=self.fileSaveInput.get('1.0', 'end-1c')
            self.currSavePath = tk.Label(height=1, width=30)
            self.currSavePath.config(text="Save Path: " + savePath)
            self.currSavePath.grid(row=2, column=1)
	
	    # the file that the info will be saved to( open appropriate one when path is specified)
            global saveFile 
            saveFile = open(r'%s' % (savePath), "w")
	
            saveFile.write("Hello saveFile\n")

	    # if opened successfully, display file close button
            if( saveFile):
                # button to close save file
                self.fileCloseButton = tk.Button(text="Close File", command=lambda:close_saveFile())
                self.fileCloseButton.grid(row=2, column=2)



        # positioning of the graphs
        self.figure1 = Figure(figsize=(6, 5), dpi=100)
        self.figure2 = Figure(figsize=(6, 5), dpi=100)

        self.plt1 = self.figure1.add_subplot(111)
        self.plt2 = self.figure2.add_subplot(111)

        self.canvas1 = FigureCanvasTkAgg(self.figure1, master=self.parent)
        self.canvas2 = FigureCanvasTkAgg(self.figure2, master=self.parent)
        # self.graph = Graph(self)
        # self.canvas = self.graph.canvas
        self.plot_widget1 = self.canvas1.get_tk_widget()
        self.plot_widget2 = self.canvas2.get_tk_widget()

        self.plot_widget1.grid(row=3, column=5)
        self.plot_widget2.grid(row=3, column=6)
        self.curve = '-51,-51,-50,-50,-50,-50,-50,-50,-50,-50,-50,-49,-49,-49,-49,-49,-49,-49,-49,-49,-49,-49,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-47,-47,-47,-47,-47,-47,-47,-47,-47,-47,-47,-47,-47,-47,-47,-47,-47,-47,-48,-48,-48,-47,-47,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-48,-49,-49,-49,-49,-49,-49,-49,-49,-49,-49,-49,-49,-49,-50,-50,-50,-50,-50,-50,-50,-50,-50,-50,-51,-51,-51,-51,-51,-51,-51,-51,-51,-51,-51,-52,-52,-52,-52,-52,-52,-52,-52,-52,-52,-52,-52,-52,-53,-53,-53,-53,-53,-53,-53,-53,-53,-53,-53,-54,-54,-54,-54,-54,-54,-54,-54,-54,-54,-54,-54,-54,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-56,-55,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-57,-56,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-57,-56,-57,-57,-57,-57,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-56,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-55,-54,-55,-54,-55,-55,-54\n'

        # self.fig.canvas.draw()

        # self.plotter = threading.Thread(target=self.plotit)
        # self.plotter.setDaemon(True) # MAKES CODE THREAD SAFE


def startSchedule():
    schedule.run()

    return


def fitScheduler(plotit):
    #
    # populate schedule

    schedule.enter(0, 1, plotit)
    schedule.enter(10, 1, plotit) # 10 seconds, priority 1, what to do
    return schedule.queue


class onlineXPMFitter(tk.Tk):
    """ Class instance of main/root window. Mainly responsible for showing the
        core components and setting other properties related to the main window."""

    def __init__(self):
        tk.Tk.__init__(self)

        # Set title and screen resolutions
        tk.Tk.wm_title(self, 'XPM Fitter')
        tk.Tk.minsize(self, width=640, height=320)
        # Optional TODO: Set a custom icon for the XPM application
        # tk.Tk.iconbitmap(self, default="[example].ico")

        # Show window and control bar
        self.graph = grafit(self)
        # self.graph.pack(side='top', fill='both', expand=True)


root = onlineXPMFitter()
root.graph.plotit()
#fitScheduler(root.graph.plotit)
#scheduThread = threading.Thread(target=startSchedule)
#scheduThread.start()
root.mainloop()
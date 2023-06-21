import tkinter as tk
import urllib.request
import time
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np


class app(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # textbox for IP address entry & request button that calls 'make_request'
        self.url_entry = tk.Text(height=1, width=30, bg='blue')
        self.url_entry.insert(tk.END, 'http://localhost:5022')
        #self.url_entry.insert(tk.END, 'http://134.79.229.21')
        self.url_entry.grid(row=1, column=1)

        # textbox for save path entry & button to set it
        self.file_path_entry = tk.Text(height=1, width=30, bg='lightblue')
        self.file_path_entry.insert(tk.END, '../../testingData/')
        self.file_path_entry.grid( row=3, column=1)

        self.start_button = tk.Button(text="Start", command=self.start_app)
        self.start_button.grid(row=5, column=1)

        self.last_updated = tk.Label(text="Last updated: N/A")
        self.last_updated.grid(row=7, column=3)

        # for the graph
        self.parent = parent
        self.figure1 = Figure(figsize=(6, 5), dpi=100)
        self.plt1 = self.figure1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.figure1, master=self.parent)
        self.plot_widget1 = self.canvas1.get_tk_widget()
        self.plot_widget1.grid(row=3, column=5)


        self.counter = 0



    def save_paths(self):
        # getting the initially defined paths
        self.url = self.url_entry.get('1.0', 'end-1c')
        self.save_path = self.file_path_entry.get('1.0', 'end-1c')

    def start_app(self):

        # keep save paths for file & url
        self.save_paths()

        #self.curr_save_path = self.save_path + 'test' + str(self.counter).zfill(3)

        self.get_and_save()



    def grab(self):
        pass
        '''
        i = 1
        while True:
            self.curr_save_path = self.save_path + 'test' + str(i).zfill(3)

            file_state = self.open_save_file()
            if file_state == True:
                self.get_and_save()
                i += 1
                # we probably don't want to use sleep... use scheduler?
                time.sleep(5)
        '''


    def get_and_save(self):
        # calls the required functions and updates the 'last updated' label

        
        #zipped = self.get_raw_data()
        self.get_raw_data()

        #self.save_data()

        # update the 'last updated' label
        current_time = dt.datetime.now().strftime("%H:%M:%S")
        self.last_updated.config(text="Last updated: " + current_time)



    def get_raw_data(self):
        # makes requests and processes data into floats
        # this request is having difficulties, check with Kolo

        self.curr_save_path = self.save_path + 'test' + str(self.counter).zfill(3)

        data = ''
        f = urllib.request.urlopen(self.url + '/?COMMAND=curve?')
        #f = requests.get(self.url + '/?COMMAND=curve?')
        data = f.read().decode()
        print('received ' + data)

        wfm = [float(u) for u in data.split(',')]

        # calling wfmpre to convert wfm to MS and VOLTS
        f2 = urllib.request.urlopen(self.url + '/?COMMAND=wfmpre?')
        #f2 = requests.get(self.url + '/?COMMAND=wfmpre?')
        wfmpre = f2.read().decode()

        # conversions to usable values
        t = [1.0e6 * (float(wfmpre.split(';')[8]) * float(i) + float(wfmpre.split(';')[10])) for i in range(0, len(wfm))]
        volt = [1.0e3 * (((float(dl) - float(wfmpre.split(';')[14]))/1.0) * float(wfmpre.split(';')[12]) - float(wfmpre.split(';')[13])) for dl in wfm]

        self.plt1.cla()
        self.plt1.plot(t, volt, 'g-')
        self.plt1.set_title("Most recent waveform")
        self.plt1.set_ylabel("MilliVolts")
        self.plt1.set_xlabel(u"Time (\u03bcs)")
        self.canvas1.draw_idle()


        

        data = np.transpose([np.array(t), np.array(volt)])

        np.savetxt(self.curr_save_path, data, delimiter=',')


        self.counter += 1

        #self.data = 
        #self.save_data()
        return zip(t, volt)


    def save_data(self):
        # a function to save the zipped data into the open file
        print(self.data)
        self.saveFile.write(self.data)

    def open_save_file(self):
        # saves the recently received data to new file
        print(self.curr_save_path)

        # this needs to be double checked
        try:
            self.saveFile = open(self.curr_save_path, 'w')
            # now things can happen to the file
            print("File opened successfully")
            return True
        except:
            print("Failed to open the file")
            return False

        # needs to be done at some point
        # saveFile.close()



class waveCapture(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        # basic setup of application
        tk.Tk.wm_title(self, 'Waveform Capture')
        tk.Tk.minsize(self, width=640, height=320)

        self.process = app(self)



root = waveCapture()
root.process.mainloop()
#root.mainloop()

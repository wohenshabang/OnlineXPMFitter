import tkinter as tk
import requests
import datetime as dt


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
        self.file_path_entry.insert(tk.END, '~/src/testingData/')
        self.file_path_entry.grid( row=3, column=1)

        self.start_button = tk.Button(text="Start", command=self.start_app)
        self.start_button.grid(row=5, column=1)

        self.last_updated = tk.Label(text="Last updated: N/A")
        self.last_updated.grid(row=7, column=3)


    def start_app(self):
        self.url = self.url_entry.get('1.0', 'end-1c')
        self.save_path = self.file_path_entry.get('1.0', 'end-1c')

        self.get_and_save()

        # THIS REPEAT ( every 5 min) IS NOT WORKING YET
        #root.after(300000, self.get_and_save)
        root.process.after(1, self.get_and_save)


    def get_and_save(self):
        # calls the required functions and updates the 'last updated' label
        # do stuff

        current_time = dt.datetime.now().strftime("%H:%M:%S")
        self.last_updated.config(text="Last updated: " + current_time)


    def get_raw_data(self):
        # makes requests and processes data into floats

        data = ''
        f = requests.get(self.url + '/?COMMAND=curve?')
        data = f.read().decode()
        print('received ' + data)

        wfm = [float(u) for u in data.split(',')]

        # calling wfmpre to convert wfm to MS and VOLTS
        f2 = requests.get(self.url + '/?COMMAND=wfmpre?')
        wfmpre = f2.read().decode()

        # conversions to usable values
        t = [1.0e6 * (float(wfmpre.split(';')[8]) * float(i) + float(wfmpre.split(';')[10])) for i in range(0, len(wfm))]
        volt = [1.0e3 * (((dl / 256) - float(wfmpre.split(';')[14])) * float(wfmpre.split(';')[12]) - float(wfmpre.split(';')[13])) for dl in wfm]

        return zip(t, volt)


    def save_to_file(self):
        # saves the recently received data to new file
        print(self.save_path)

        # this needs to be double checked
        try:
            saveFile = open(self.save_path, 'w')
            # now things can happen to the file
            print("File opened successfully")
        except:
            print("Failed to open the file")

        # needs to be done at some point
        saveFile.close()



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

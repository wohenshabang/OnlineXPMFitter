import tkinter as tk
import requests


class app(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.url_entry = tk.Text(height=1, width=30, bg='blue')
        self.url_entry.grid(row=1, column=1)
        self.req_button = tk.Button(text="Make Request", command=self.make_request)
        self.req_button.grid(row=1, column=2)


    def make_request(self):
        url = self.url_entry.get('1.0', 'end-1c')
        #response = requests.get(url)
        print(url)
        #self.text.insert('1.0', response.text)



class waveCapture(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        tk.Tk.wm_title(self, 'Waveform Capture')
        tk.Tk.minsize(self, width=640, height=320)

        self.process = app(self)



root = waveCapture()
root.process.mainloop()
#root.mainloop()

import tkinter as tk
import requests


class app(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        #self.file_path = filedialog.asksaveasfilename(initialdir = "/", title = "Select file", filetypes = (("Text files", "*.txt"), ("all files", "*.*"))

        # textbox for save path entry & button to set it
        self.file_path_entry = tk.Text(height=1, width=30, bg='lightblue')
        self.file_path_entry.grid( row=3, column=1)
        self.set_save_path_button = tk.Button(text="Set Save Path", command=self.set_save_path)
        self.set_save_path_button.grid(row=3, column=2)

        # textbox for IP address entry & request button that calls 'make_request'
        self.url_entry = tk.Text(height=1, width=30, bg='blue')
        self.url_entry.grid(row=1, column=1)
        self.req_button = tk.Button(text="Make Request", command=self.make_request)
        self.req_button.grid(row=1, column=2)


    def make_request(self):
        # reads contents of 'url_entry' field and makes request
        url = self.url_entry.get('1.0', 'end-1c')
        #response = requests.get(url)
        print(url)
        #self.text.insert('1.0', response.text)

    def set_save_path(self):
        # reads contents of 'file_path_entry' field and opens file
        save_path = self.file_path_entry.get('1.0', 'end-1c')
        print(save_path)

        # this needs to be double checked
        try:
            saveFile = open(save_path, 'w')
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

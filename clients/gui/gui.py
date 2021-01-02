# helloworld.py
import tkinter as tk
import pygubu

#Folder with hp3478a.py/prologix.py must be in PYTHONPATH
#Alternatively copy them to this folder
from hp3478a import hp3478a
from time import sleep

port = "/dev/ttyACM0"

test = hp3478a(23, port, debug=True)

test.getStatus()

class HelloWorldApp:
    
    def __init__(self):

        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('../gui.ui')

        #3: Create the mainwindow
        self.mainwindow = builder.get_object('Frame_1')
        self.builder.get_object('Label_1').after(1000,self.update) 
        
    def run(self):
        self.mainwindow.mainloop()

    def update(self):
        global test
        labelM = self.builder.get_object('Label_1')
        labelF = self.builder.get_object('Label_2')
        labelR = self.builder.get_object('Label_3')

        measure = float(test.getMeasure())
        suffix = ""
        if measure < 1:
            measure = measure * 1000
            suffix = "m"
            print("<1000 - " + suffix + " - now: " + str(measure))
            if measure < 1:
                measure = measure * 1000
                suffix = "µ"
                print("<1000 - " + suffix + " - now: " + str(measure))
                if measure < 1:
                    measure = measure * 1000
                    suffix = "n"
                    print("<1000 - " + suffix + " - now: " + str(measure))
        elif measure > 1000:
            measure = measure / 1000
            suffix = "k"
            if measure > 1000:
                measure = measure / 1000
                suffix = "M"
                if measure > 1000:
                    measure = measure / 1000
                    suffix = "G"

        measure = str(measure) + suffix

        labelM.configure(text = measure)
        labelF.configure(text = test.getFunction())
        labelR.configure(text = test.getRange())
        labelM.after(1000,self.update) 


if __name__ == '__main__':
    app = HelloWorldApp()
    app.run()

from prologix import prologix

port = "/dev/ttyACM0"

class hp3478a(object):

    addr = None
    gpib = None

    def __init__(self, addr, port=None, baud=921600, timeout=0.25, prologixGpib=None, debug=False):
        if port == None and prologixGpib == None:
            print("!! You must supply either a serial port or a prologix object")

        if prologixGpib == None:
            self.gpib = prologix(port=port, baud=baud, timeout=timeout, debug=debug)
        else:
            self.gpib = prologixGpib
        


test = hp3478a(22, port, debug=True)
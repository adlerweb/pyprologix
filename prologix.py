import serial
import datetime
import os

class prologix(object):
    '''
    Class for handling prologix protocol based GPIB communication
    Based on code by Daniel Stadelmann and Tobias Badertscher
    '''

    serial = None
    debug = False
    EOL = "\n"

    def __init__(self, port, baud=921600, timeout=0.25, debug=False):
        if timeout==None:
            timeout=2

        self.debug = debug

        #Establish connection
        try:
            self.serial = serial.Serial(port, baudrate=baud, timeout=timeout)
        except serial.SerialException:
            print("!! Port " + port + " could not be opened")
            self.serial = None
            return None

        #Check for Prologix device
        check = self.cmdPoll("++ver", read=False)
        if len(check)<=0:
            print("!! No responding device on port " + port + " found")
            self.serial = None
            return None
        elif not "Prologix".casefold() in check.casefold():
            print("!! Device on Port " + port + " does not seem to be Prologix compatible")
            print(check)
            self.serial = None
            return None
        elif debug:
            print(".. Found Prologix compatible device on port " + port)

        #Initialize basic parameters
        self.cmdWrite("++mode 1")           # Change to controller mode
        self.cmdWrite("++auto 0")           # Do not automatically read device after each command
        self.cmdWrite("++eoi 0")            # Do not assert EOI after commandI
        self.cmdWrite("++eos 0")            # Append CR+LF to all commands
        self.cmdWrite("++eot_enable 0")     # Do not append EOT to USB output after EOI
        self.cmdWrite("++read_tmo_ms 2500") # Transmission timeout
        self.cmdWrite("++ifc")              # Assert IFC to indicate we're taking control of the bus

    def cmdWrite(self, cmd, addr=None):
        if addr != None:
            self.cmdWrite("++addr " + str(addr), addr=None)
        self.serial.write(str.encode(cmd+self.EOL))
        if self.debug:
            print(">> " + cmd)
        self.serial.flush()

    def cmdPoll(self, cmd, addr=None, binary=False, read=True):
        self.serial.reset_input_buffer()
        self.cmdWrite(cmd, addr)
        if read:
            self.cmdWrite("++read eoi", None)
        out = self.serial.readline()
        if not binary:
            out = out.decode()
            out = out.strip()
            if self.debug and len(out) > 0:
                print("<< " + out)
        elif self.debug and len(out) > 0:
            for b in out:
                print("<< 0b" + format(b, '08b'))
        return out

    def cmdClr(self, addr=None):
        self.cmdWrite("++clr", addr)
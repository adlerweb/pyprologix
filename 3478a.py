
from prologix import prologix
from dataclasses import dataclass
import datetime

port = "/dev/ttyACM0"

class hp3478a(object):

    @dataclass
    class hp3478aStatus:
        function: int = None
        range: int = None
        digits: float = None
        triggerExternal: bool = None
        calRAM: bool = None
        frontPorts: bool = None
        freq50Hz: bool = None
        autoZero: bool = None
        autoRange: bool = None
        triggerInternal: bool = None
        srqPon: bool = None
        srqCalFaled: bool = None
        srqKbd: bool = None
        srqHWErr: bool = None
        srqSyntaxErr: bool = None
        srqReading: bool = None
        errADLink: bool = None
        errADSelfTest: bool = None
        errADSlope: bool = None
        errROM: bool = None
        errRAM: bool = None
        errChecksum: bool = None
        dac: int = None
        fetched: datetime = None

    addr = None
    gpib = None
    status = hp3478aStatus()

    def __init__(self, addr, port=None, baud=921600, timeout=0.25, prologixGpib=None, debug=False):
        if port == None and prologixGpib == None:
            print("!! You must supply either a serial port or a prologix object")

        if prologixGpib == None:
            self.gpib = prologix(port=port, baud=baud, timeout=timeout, debug=debug)
        else:
            self.gpib = prologixGpib

    def getMeasure(self):
        return float(self.gpib.cmdPoll(" ", self.addr))

    def getStatus(self):
        status = self.gpib.cmdPoll("B", binary=True)
        
        #Update last readout time
        self.status.fetched = datetime.datetime.now()

        #Byte 5: RAW DAC value
        self.status.dac = status[4]

        #Byte 4: Error Information
        self.status.errChecksum     = (status[3]&(1<<0) != 0)
        self.status.errRAM          = (status[3]&(1<<1) != 0)
        self.status.errROM          = (status[3]&(1<<2) != 0)
        self.status.errADSlope      = (status[3]&(1<<3) != 0)
        self.status.errADSelfTest   = (status[3]&(1<<4) != 0)
        self.status.errADLink       = (status[3]&(1<<5) != 0)

        #Byte 3: Serial Poll Mask
        self.status.srqReading      = (status[2]&(1<<0) != 0)
            #Bit 1 not used
        self.status.srqSyntaxErr    = (status[2]&(1<<2) != 0)
        self.status.srqHWErr        = (status[2]&(1<<3) != 0)
        self.status.srqKbd          = (status[2]&(1<<4) != 0)
        self.status.srqCalFaled     = (status[2]&(1<<5) != 0)
            #Bit 6 always zero
        self.status.srqPon          = (status[2]&(1<<7) != 0)

        #Byte 2: Status Bits
        self.status.triggerInternal = (status[1]&(1<<0) != 0)
        self.status.autoRange       = (status[1]&(1<<1) != 0)
        self.status.autoZero        = (status[1]&(1<<2) != 0)
        self.status.freq50Hz        = (status[1]&(1<<3) != 0)
        self.status.frontPorts      = (status[1]&(1<<4) != 0)
        self.status.calRAM          = (status[1]&(1<<5) != 0)
        self.status.triggerExternal = (status[1]&(1<<6) != 0)

        #Byte 1: Function/Range/Digits
        sb1 = status[0]
        self.status.digits = (sb1 & 0b00000011)
        sb1 = sb1 >> 2
        self.status.range = (sb1 & 0b00000111)
        sb1 = sb1 >> 3
        self.status.function = (sb1 & 0b00000111)

        return self.status
        


test = hp3478a(22, port, debug=True)

print(test.getMeasure())
print(test.getStatus())
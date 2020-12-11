from prologix import prologix
from dataclasses import dataclass
import datetime

class hp3478a(object):
    """Control HP3478A multimeters using a Prologix compatible dongle

    Attributes
    ----------

    addr : int
        Address of the targeted device
    gpib : prologix
        Prologix object used to communicate with the prologix dongle
    status : hp3478aStatus
        Current device status
    """

    addr: int = None
    gpib: prologix = None

    VDC  = 1
    VAC  = 2
    Ω2W  = 3
    Ω4W  = 4
    ADC  = 5
    AAC  = 6
    EXTΩ = 7

    TRIG_INT = 1
    TRIG_EXT = 2
    TRIG_SIN = 3
    TRIG_HLD = 4
    TRIG_FST = 5

    @dataclass
    class hp3478aStatus:
        """Current device status

        Attributes
        ----------
        function : int
            numeric representation of currently used measurement function:
            1: DC Voltage
            2: AC Voltage
            3: 2-Wire Resistance
            4: 4-Wire Resistance
            5: DC Current
            6: AC Current
            7: Extended Ohms
            see also: getFunction
        range : int
            numeric representation of currenly used measurement range:
            1: 30mV DC, 300mV AC, 30Ω, 300mA, Extended Ohms
            2: 300mV DC, 3V AC, 300Ω, 3A
            3: 3V DC, 30V AC, 3kΩ
            4: 30V DC, 300V AC, 30kΩ
            5: 300V DC, 300kΩ
            6: 3MΩ
            7: 30MΩ
            see also: getRange
        digits : int
            numeric representation of selected measurement resolution:
            1: 5½ Digits
            2: 4½ Digits
            3: 3½ Digits
            Lower resoluton allows for faster measurements
            see also: getDigits
        triggerExternal : bool
            External trigger enabled
        
        calRAM : bool
            Cal RAM enabled
        frontProts : bool
            Front/Read switch selected front measurement connectors
            True = Front Port
        freq50Hz : bool
            Device set up for 50Hz operation. False = 60Hz.
        autoZero : bool
            Auto-Zero is enabled
        autoRange : bool
            Auto-Range is enabled
        triggerInternal : bool
            Internal trigger is enabled. False = Single trigger.
        
        srqPon : bool
            Device asserts SRQ on power-on or Test/Reset/SDC
            Controlled by rear configuration switch 3
        srqCalFailed : bool
            Device asserts SRQ if CAL procedure failes
        srqKbd : bool
            Device asserts SRQ if keyboar SRQ is pressed
        srqHWErr : bool
            Device asserts SRQ if a hardware error occurs
        srqSyntaxErr : bool
            Device asserts SRQ if a syntax error occurs
        srqReading : bool
            Device asserts SRQ every time a new reading is available
        
        errADLink: bool
            Error while communicating with aDC
        errADSelfTest: bool
            ADC failed internal self-test
        errADSlope: bool
            ADC slope error
        errROM: bool
            ROM self-test failed
        errRAM: bool
            RAM self-test failed
        errChecksum: bool
            Self-test detecten an incorrect CAL RAM checksum
            Re-Asserted every time you use an affected range afterwards

        dac: int
            Raw DAC value

        fetched: datetime
            Date and time this status was updated
        """
        function: int = None
        range: int = None
        digits: int = None
        triggerExternal: bool = None
        calRAM: bool = None
        frontPorts: bool = None
        freq50Hz: bool = None
        autoZero: bool = None
        autoRange: bool = None
        triggerInternal: bool = None
        srqPon: bool = None
        srqCalFailed: bool = None
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
    status = hp3478aStatus()

    def __init__(self, addr: int, port: str=None, baud: int=921600, timeout: float=0.25, prologixGpib: prologix=None, debug: bool=False):
        """

        Parameters
        ----------
        addr : int
            Address of the targeted device
        port : str, optional
            path of the serial device to use. Example: `/dev/ttyACM0` or `COM3`
            If set a new prologix instance will be created
            Either port or prologixGpib must be given
            by default None
        baud : int, optional
            baudrate used for serial communication
            only used when port is given
            921600 should work with most USB dongles
            115200 or 9600 are common for devices using UART in between
            by default 921600
        timeout : float, optional
            number of seconds to wait at maximum for serial data to arrive
            only used when port is given
            by default 2.5 seconds
        prologixGpib : prologix, optional
            Prologix instance to use for communication
            Ths may be shared between multiple devices with different addresses
            Either port or prologixGpib must be given
            by default None
        debug : bool, optional
            Whether to print verbose status messages and all communication
            by default False
        """
        if port == None and prologixGpib == None:
            print("!! You must supply either a serial port or a prologix object")

        if prologixGpib is None:
            self.gpib = prologix(port=port, baud=baud, timeout=timeout, debug=debug)
        else:
            self.gpib = prologixGpib

    def getMeasure(self) -> float:
        """Get last measurement as float

        Returns
        -------
        float
            last measurement
        """
        return float(self.gpib.cmdPoll(" ", self.addr))

    def getDigits(self, digits: int=None) -> float:
        """Get a human readable representation of currently used resolution

        Parameters
        ----------
        digits : int, optional
            numeric representation to interpret
            If None is given the last status reading is used
            by default None

        Returns
        -------
        str|None
            3.5, 4.5 or 5.5 for the current resolution
            None for invalid numbers
        """
        if digits is None:
            digits = self.status.digits

        if digits == 1:
            return 5.5
        elif digits == 2:
            return 4.5
        elif digits == 3:
            return 3.5
        return None
    
    def getFunction(self, function: int=None) -> str:
        """Get a human readable representation of currently used measurement function

        Parameters
        ----------
        function : int, optional
            numeric representation to interpret
            If None is given the last status reading is used
            by default None

        Returns
        -------
        str|None
            VDC for DC Volts
            ADC for AC Volts
            Ω2W for 2-Wire Resistance
            Ω4W for 4-Wire Resistance
            ADC for DC Current
            AAC for AC Current
            ExtΩ for extended Ohms
            None for invalid numbers

        """
        if function is None:
            function = self.status.function

        if function == 1:
            return "VDC"
        elif function == 2:
            return "VAC"
        elif function == 3:
            return "Ω2W"
        elif function == 4:
            return "Ω4W"
        elif function == 5:
            return "ADC"
        elif function == 6:
            return "AAC"
        elif function == 7:
            return "ExtΩ"
        else:
            return None
    
    def getRange(self, range: int=None, function: int=None, numeric: bool=False):
        """Get a human readable representation of currently used measurement range

        Parameters
        ----------
        range : int, optional
            numeric range representation to interpret
            If None is given the last status reading is used
            by default None
        function : int, optional
            numeric function representation to interpret
            If None is given the last status reading is used
            by default None
        numeric : bool, optional
            If True return the maximum value as Float instead
            of a human readable verison using SI-prefixes

        Returns
        -------
        str|float|None
            Maximum measurement value in current range
        """
        if range is None:
            range = self.status.range
        if function is None:
            function = self.status.function
        
        if range == 1:
            if function == 1:
                if numeric:
                    return 0.03
                else:
                    return "30mV"
            elif function == 2:
                if numeric:
                    return 0.3
                else:
                    return "300mV"
            elif function == 3 or function == 4:
                if numeric:
                    return 30.0
                else:
                    return "30Ω"
            elif function == 5 or function == 6:
                if numeric:
                    return 0.3
                else:
                    return "300mA"
            else:
                return None
        elif range == 2:
            if function == 1:
                if numeric:
                    return 0.3
                else:
                    return "300mV"
            elif function == 2:
                if numeric:
                    return 3.0
                else:
                    return "3V"
            elif function == 3 or function == 4:
                if numeric:
                    return 300.0
                else:
                    return "300Ω"
            elif function == 5 or function == 6:
                if numeric:
                    return 3.0
                else:
                    return "3A"
            else:
                return None
        elif range == 3:
            if function == 1:
                if numeric:
                    return 3.0
                else:
                    return "3V"
            elif function == 2:
                if numeric:
                    return 30.0
                else:
                    return "30V"
            elif function == 3 or function == 4:
                if numeric:
                    return 3000.0
                else:
                    return "3kΩ"
            else:
                return None
        elif range == 4:
            if function == 1:
                if numeric:
                    return 30.0
                else:
                    return "30V"
            elif function == 2:
                if numeric:
                    return 300.0
                else:
                    return "300V"
            elif function == 3 or function == 4:
                if numeric:
                    return 30000.0
                else:
                    return "30kΩ"
            else:
                return None
        elif range == 5:
            if function == 1:
                if numeric:
                    return 300.0
                else:
                    return "300V"
            elif function == 3 or function == 4:
                if numeric:
                    return 300000.0
                else:
                    return "300kΩ"
            else:
                return None
        elif range == 6:
            if function == 3 or function == 4:
                if numeric:
                    return 3000000.0
                else:
                    return "3MΩ"
            else:
                return None
        elif range == 7:
            if function == 3 or function == 4:
                if numeric:
                    return 30000000.0
                else:
                    return "30MΩ"
            else:
                return None

    def getStatus(self) -> hp3478aStatus:
        """Read current device status and populate status object

        Returns
        -------
        hp3478aStatus
            Updated status object
        """
        status = self.gpib.cmdPoll("B", self.addr, binary=True)
        
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
        self.status.srqCalFailed    = (status[2]&(1<<5) != 0)
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

    def getFrontRear(self) -> bool:
        """Get position of Front/Rear switch

        May also be used to easily determine if the device is responding

        Returns
        -------
        bool
            True  -> Front-Port
            False -> Rear-Port
            None  -> Device did not respond
        """
        check = self.gpib.cmdPoll("S")
        if check == 1:
            return True
        elif check == 0:
            return False
        else:
            return None

    def setAutoZero(self, autoZero: bool, noUpdate: bool=False) -> bool:
        """change Auto-Zero setting

        Parameters
        ----------
        autoZero : bool
            Whether to enable or disable Auto-Zero
        noUpdate : bool, optional
            If True do not update status object to verify change was successful
            by default False

        Returns
        -------
        bool
            new status of autoZero; presumed status if `noUpdate` was True
        """
        setVal = 0
        if autoZero: setVal = 1

        self.gpib.cmdWrite("Z"+str(autoZero), self.addr)

        if noUpdate:
            if self.gpib.debug:
                print(".. AutoZero changed to " + setVal + " without verification.")
            return setVal
        else:
            self.getStatus()
            if autoZero != self.status.autoZero:
                print("!! Error while changing AutoZero - tried to set " + str(autoZero) + " but verification was " + str(self.status.autoZero))
            elif self.gpib.debug:
                print(".. AutoZero successfully changed to " + str(self.status.autoZero))
            return self.status.autoZero

    def setDisplay(self, text: str=None, online: bool=True) -> bool:
        """Change device display

        Parameters
        ----------
        text : str, optional
            When text is None or empty device will resume standard display mode
                as in show measurements
            When text is set it will be displayed on the device
            
            Only ASCII 32-95 are valid. Function aborts for invalid characters
            Must be <= 12 Characters while , and . do not count as character.
                consecutive , and . may not work
                using . or , after character 12 may not work
                Function aborts for too long strings
        online : bool, optional
            When True the device just shows the text but keeps all functionality online
            When False the device will turn off all dedicated annunciators and stop updating
                the display once the text was drwn. This will free up ressources and enable
                faster measurement speeds. Using False takes about 30mS to complete. If the
                updating is stopped for over 10 minutes if will shut down as in blank screen.
            by default True

        Returns
        -------
        bool
            Wheather setting the text worked as expected
        """
        if text is None or text == "":
            # Reset display
            self.gpib.cmdWrite("D1", self.addr)
            if self.gpib.debug:
                print("Display reset to standard mode")
            return True
        
        len = 0
        for c in text:
            if ord(c) < 32 or ord(c) > 95:
                print("!! Character '" + c + "' is not supported")
                return False
            if c != "," and c != ".":
                len = len+1
            
            if len > 12:
                print("!! Text too long; max 12 characters")
                return False
            
        cmd = "D2"
        dt = ""
        if not online:
            cmd = "D3"
            dt = " (updates paused)"

        self.gpib.cmdWrite(cmd + text, self.addr)
        
        if self.gpib.debug:
            print(".. Display changed to '" + text + "'" + dt)

        #@TODO we could check status/errors to catch syntax errors here
        return True

    def setFunction(self, function : int, noUpdate: bool=False) -> bool:
        """Change current measurement function

        Parameters
        ----------
        function : int
            numeric function representation
            you may also use the following class constants:
                VDC,VAC,Ω2W,Ω4W,ADC,AAC,EXTΩ
        noUpdate : bool, optional
            If True do not update status object to verify change was successful
            by default False

        Returns
        -------
        bool
            Whether update succeeded or not; not verified if `noUpdate` was True
        """
        if function <= 0 or function > 7:
            print("!! Invalid function")
            return False
        
        self.gpib.cmdWrite("F" + str(function), self.addr)

        if not noUpdate:
            self.getStatus()
            if self.status.function != function:
                print("!! Set failed. Tried to set " + self.getFunction(function) + " but device returned " + self.getFunction(self.status.function))
                return False
            elif self.gpib.debug:
                print(".. Changed to function " + self.getFunction(function))
        elif self.gpib.debug:
            print(".. Probably changed to function " + self.getFunction(function))
        
        return True

    def setRange(self, range : str, noUpdate : bool=False) -> bool:
        """Change current measurement range

        Parameters
        ----------
        range : str|float
            Range as SI-Value or float
            Valid values:
            A or AUTO to enable Auto-Range
            30m,300m,3,30,300,3k,30k,300k,3M,30M
            0.03,0.3,3,30,300,3000,30000,300000,3000000,30000000
            Not all ranges can be used in all measurement functions
        noUpdate : bool, optional
            If True do not update status object to verify change was successful
            by default False

        Returns
        -------
        bool
            Whether update succeeded or not; not verified if `noUpdate` was True
        """
        newRange = None
        newRangeF = None
        if range == "30m"       or range == 0.03:
            newRange  = -2
            newRangeF = 0.03
        elif range == "300m"    or range == 0.3:
            newRange  = -1
            newRangeF = 0.3
        elif range == "3"       or range == 3:
            newRange  = 0
            newRangeF = 3
        elif range == "30"      or range == 30:
            newRange  = 1
            newRangeF = 30
        elif range == "300"     or range == 300:
            newRange  = 2
            newRangeF = 300
        elif range == "3k"      or range == 3000:
            newRange  = 3
            newRangeF = 3000
        elif range == "30k"     or range == 30000:
            newRange  = 4
            newRangeF = 30000
        elif range == "300k"    or range == 300000:
            newRange  = 5
            newRangeF = 300000
        elif range == "3M"      or range == 3000000:
            newRange  = 6
            newRangeF = 3000000
        elif range == "30M"     or range == 30000000:
            newRange  = 7
            newRangeF = 30000000
        elif range.lower() == "a" or range.lower() == "auto":
            newRange = "A"
        
        if newRange is None:
            print("!! Invalid range")
            return False
        
        self.gpib.cmdWrite("R" + str(newRange), self.addr)

        if not noUpdate:
            self.getStatus()
            if newRange == "A":
                if not self.status.autoRange:
                    print("!! Tried to enable Auto-Range but device refused")
                    return False
                elif self.gpib.debug:
                    print(".. Enabled Auto-Range")
            else:
                newRangeC = self.getRange(numeric=True)
                if newRangeF != newRangeC:
                    print("!! Tried to set range to " + str(range) + " but device reported " + self.getRange())
                    return False
                elif self.gpib.debug:
                    print(".. Set range to " + self.getRange())
        elif self.gpib.debug:
            print(".. Probably changed to range " + str(range))
        
        return True

    def setDigits(self, digits : float, noUpdate : bool=False) -> bool:
        """Change current measurement resolution

        Parameters
        ----------
        digits : float
            desired measurement resolution
            Valid values: 3,3.5,4,4.5,5,5.5
        noUpdate : bool, optional
            If True do not update status object to verify change was successful
            by default False

        Returns
        -------
        bool
            Whether update succeeded or not; not verified if `noUpdate` was True
        """
        newDigits = None
        if digits == 3 or digits == 3.5:
            newDigits = "3"
        elif digits == 4 or digits == 4.5:
            newDigits = "4"
        elif digits == 5 or digits == 5.5:
            newDigits = "5"
        else:
            print("!! Invalid digits")
            return False

        self.gpib.cmdWrite("N"+newDigits, self.addr)

        if not noUpdate:
            self.getStatus()
            if int(self.getDigits()) != int(newDigits):
                print("!! Tried to set digits to " + str(int(newDigits)) + "½ but device reported " + str(int(self.getDigits())) + "½")
                return False
            elif self.gpib.debug:
                print(".. Set digits to " + str(int(self.getDigits())) + "½")
        elif self.gpib.debug:
            print(".. Probably changed digits to " + str(int(self.getDigits())) + "½")
        
        return True

    def setTrigger(self, trigger : int, noUpdate : bool=False) -> bool:
        """Change current measurement trigger

        Parameters
        ----------
        trigger : int
            desired trigger mode
            1 or TRIG_INT -> Automatic internal trigger
            2 or TRIG_EXT -> Abort current measurements; Start on LOW-edge or via GPIB
            3 or TRIG_SIN -> Complete current measurement. New one on GPIB GET
            4 or TRIG_HLD -> Abort current measurement. New one on GPIB GET
            5 or TRIG_FST -> Same as TRIG_SIN but skip settling delay for AC

        noUpdate : bool, optional
            If True do not update status object to verify change was successful
            by default False

        Returns
        -------
        bool
            Whether update succeeded or not; not verified if `noUpdate` was True
        """
        if trigger <= 0 or trigger > 5:
            print("!! Invalid digits")
            return False

        self.gpib.cmdWrite("T" + str(trigger), self.addr)

        if not noUpdate:
            self.getStatus()
            if trigger == self.TRIG_EXT and not self.status.triggerExternal:
                print("!! Tried to enable external trigger but flag did not update")
                return False
            elif trigger == self.TRIG_SIN and self.status.triggerInternal:
                print("!! Tried to enable singe trigger but auto trigger flag is still active")
                return False
            elif trigger == self.TRIG_INT and not self.status.triggerInternal:
                print("!! Tried to enable internal trigger but auto trigger flag is not active")
                return False
            elif trigger == self.TRIG_HLD and self.status.triggerInternal:
                print("!! Tried to enable trigger hold but auto trigger flag is still active")
                return False
        
        if self.gpib.debug:
            print(".. Probably changed trigger to " + str(trigger))
        
        return True

    def setSRQ(self, srq:int):
        """Set Serial Poll Register Mask

        @TODO Not tested and no validations

        Parameters
        ----------
        srq : int
            Parameter must be two digits exactlz. Bits 0-5 of the binary representation
            are used to set the mask
        """
        self.gpib.cmdWrite(srq, self.addr)

    def clearSPR(self):
        """Clear Serial Poll Register (SPR)
        """
        self.gpib.cmdWrite("K", self.addr)

    def clearERR(self) -> bytearray:
        """Clear Error Registers

        Returns
        -------
        bytearray
            Error register as octal digits
        """
        return self.gpib.cmdPoll("E", self.addr, binary=True)

    def callReset(self):
        """Reset the device
        """
        self.gpib.cmdClr(self.addr)

import serial
import datetime
import os

class prologix(object):
    """Class for handling prologix protocol based GPIB communication

    Based on code by Daniel Stadelmann and Tobias Badertscher

    Attributes
    ----------
    serial : object
        PySerial object used to communicate with the prologix dongle
    debug : bool
        Whether to print verbose status messages and all communication
    timeout : float
        Timeout for serial and GPIB operations
    EOL : str
        Characters to append to all commands sent to USB

    """

    serial: object = None
    debug: bool = False
    timeout: float = 2.5
    EOL: str = "\n"

    def __init__(self, port: str, baud: int=921600, timeout: float=2.5, debug: bool=False):
        """

        Parameters
        ----------
        port : str
            path of the serial device to use. Example: `/dev/ttyACM0` or `COM3`
        baud : int, optional
            baudrate used for serial communication
            921600 should work with most USB dongles
            115200 or 9600 are common for devices using UART in between
            by default 921600
        timeout : float, optional
            number of seconds to wait at maximum for serial data to arrive
            by default 2.5 seconds
        debug : bool, optional
            Whether to print verbose status messages and all communication
            by default False

        """
        if timeout is not None:
            self.timeout = timeout

        self.debug = debug

        #Establish connection
        try:
            self.serial = serial.Serial(port, baudrate=baud, timeout=self.timeout)
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
        self.cmdWrite("++mode 1")                               # Change to controller mode
        self.cmdWrite("++auto 0")                               # Do not automatically read device after each command
        self.cmdWrite("++eoi 0")                                # Do not assert EOI after commandI
        self.cmdWrite("++eos 0")                                # Append CR+LF to all commands
        self.cmdWrite("++eot_enable 0")                         # Do not append EOT to USB output after EOI
        self.cmdWrite("++read_tmo_ms " + str(self.timeout))     # Transmission timeout
        self.cmdWrite("++ifc")                                  # Assert IFC to indicate we're taking control of the bus

    def cmdWrite(self, cmd: str, addr: int=None):
        """Write a single, returnless command to a GPIB device

        Parameters
        ----------
        cmd : str
            The command string to be sent
        addr : int, optional
            address of the targeted device. If set an `++addr` will be issued first
            by default None
        """
        if addr is not None:
            """
            @TODO we probably could skip addr if this is equal to the last addr call and 
            we're sure noone else is using the bus to reduce bus load.
            """
            self.cmdWrite("++addr " + str(addr), addr=None)
        self.serial.write(str.encode(cmd+self.EOL))
        if self.debug:
            print(">> " + cmd)
        self.serial.flush()

    def cmdPoll(self, cmd: str, addr: int=None, binary: bool=False, read: bool=True):
        """Write a single command to a GPIB device and fetch response

        Parameters
        ----------
        cmd : str
            The command string to be sent
        addr : int, optional
            address of the targeted device. If set an `++addr` will be issued first
            by default None
        binary : bool, optional
            If False responses are decoded and returned as String
            If True resonses are unchanged and returned as byte array
            by default False
        read : bool, optional
            Whether to issue a `++read eoi` before waiting for data
            While required for GPIB device commands internal prologix commands
                or while operating with `++auto 1` might return data without polling
                first
            by default True

        Returns
        -------
        None|str|bytearray
            None for empty responses
            str or bytearray depending on `binary` parameter
        """
        self.serial.reset_input_buffer()
        self.cmdWrite(cmd, addr)
        if read:
            self.cmdWrite("++read eoi", None)
        out = self.serial.readline()
        if len(out) == 0:
            return None
        if not binary:
            out = out.decode()
            out = out.strip()
            if self.debug and len(out) > 0:
                print("<< " + out)
        elif self.debug and len(out) > 0:
            for b in out:
                print("<< 0b" + format(b, '08b'))
        return out

    def cmdClr(self, addr: int=None):
        """Send `SDC` (selected device clear) to device

        Parameters
        ----------
        addr : int, optional
            address of the targeted device. If set an `++addr` will be issued first
            by default None
        """
        self.cmdWrite("++clr", addr)

    def escapeCmd(self, cmd : str) -> str:
        """Escape device command so they traverse the Prologix protocol

        Parameters
        ----------
        cmd : str
            command to send

        Returns
        -------
        str
            escaped command to send
        """
        out = ""
        for c in cmd:
            if c == chr(10) or c == chr(13) or chr(27) or chr(43):
                c = chr(27)+c
            out = out + c
        return out
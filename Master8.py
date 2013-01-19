#!/usr/bin/env python
"""Interface with AMPI Master-8 Stimulators"""

import serial

__author__  = 'Christopher J. Johnson <effigies@bu.edu>'
__version__ = 0.1

# ASCII codes for Master 8 Keys
# Duplicates exist to accommodate all references in the manuals
DURA = DURATION         = "D"
INTERVAL                = "I"
DELAY                   = "L"
M                       = "M"
V                       = "V"
J = JUMP = DELTAV       = "J"
FREE = FREE_RUN         = "F"
TRAIN                   = "N"
TRIG                    = "G"
DC                      = "C"
GATE                    = "T"
OFF                     = "O"
TIMER                   = "W"
ALL                     = "A"
CLOCK_DISP              = "Q"
STOP_WATCH              = "S"
CLOCK_RESET             = "R"
CHECK                   = "H"
CLEAR_DISP              = "Y"
CONNECT = CNCT_DSCNCT   = "X"
DISCONNECT              = "Z"
ENTER                   = "E"
BEGIN                   = "B"

cmOff, cmFreeRun, cmTrain, cmTrig, cmDC, cmGate = range(6)

class Master8(object):
    """An attempt to replicate the Master 8 SDK as closely as possible
    in Python.
    
    At present, the following features are known to be missing:
        - Automatic connection to Master 8 device (Python serial
          connection needed)
        - connect method
        - Boolean return values reporting success
        - Connections to combination channels are not supported

    None of these should be difficult, but they are not important to my
    use and my access to a Master 8 is sporadic.
    
    The Master 8 SDK assumes a Windows machine, so comparisons cannot
    readily be made with our equipment. This library ought to run on
    Windows, though."""

    # Ranges of valid parameters for various functions
    paradigms = range(1,9)
    channels = range(1,9) # XXX Ignores additive channels

    # Replicate the integer cm* modes and their corresponding codes
    cmList = range(6)
    modes = [OFF, FREE_RUN, TRAIN, TRIG, DC, GATE]

    def __init__(self, connection=None):
        if connection == None:
            # XXX Should attempt to find Master 8; cannot test without one
            self.c = serial.Serial()
        elif type(connection) == str:
            self.c = serial.serial_for_url(connection)
        elif serial.serialutil.SerialBase in type.mro(type(connection)):
            self.c = connection
        else:
            print "Unknown connection: %s" % repr(connection)

    def write(self, *args):
        """Translate list of arguments to a command string and send to
        device"""
        self.c.write(' '.join(map(str,args)))

    def writeInterval(self, f, minf=0, maxf=3999, res=6):
        """Write a length of time to the Master 8. Intervals can be
        specified to microsecond resolution.
        
        Parameters:
            f       - floating point representation of interval
            minf    - minimum allowable inteval
            minf    - maximum allowable inteval
            res     - number of decimal points to truncate interval
        """
        if minf is not None:
            assert(f >= minf)
        if maxf is not None:
            assert(f <= maxf)
        f_ = "{{0:0.{0:d}f}}".format(res).format(f).rstrip('0').rstrip('.')
        self.write(f_, ENTER, 0, ENTER)
    
    def writeVoltage(self, f, minf=-12.7, maxf=12.7, res=1):
        """Write a voltage to the Master 8. Voltages can be specified to
        0.1V resolution.
        
        Parameters:
            f       - floating point representation of voltage
            minf    - minimum allowable voltage
            minf    - maximum allowable voltage
            res     - number of decimal points to truncate voltage
        """
        if minf is not None:
            assert(f >= minf)
        if maxf is not None:
            assert(f <= maxf)

        self.write(round(abs(f),res), ENTER)

        if f < 0:
            self.write('-')

        self.write(ENTER)

    @property
    def connected(self):
        """True if connected
        Setting to a false value closes the connection"""
        return self.c.isOpen()

    @connected.setter
    def connected(self, value):
        if not value:
            self.c.close()

    def changeParadigm(self, paradigm):
        assert(paradigm in self.paradigms)
        self.write(ALL, paradigm, ENTER)

    def changeChannelMode(self, channel, mode):
        assert(channel in self.channels)
        if mode in self.cmList:
            self.write(self.modes[mode], channel, ENTER)
        elif mode in self.modes:
            self.write(mode, channel, ENTER)
        else:
            assert(mode in self.cmList or mode in self.modes)

    def setChannelDuration(self, channel, duration):
        self.write(DURATION, channel)
        self.writeInterval(duration, minf=40e-6)

    def setChannelInterval(self, channel, interval):
        self.write(INTERVAL, channel)
        self.writeInterval(interval, minf=60e-6)

    def setChannelDelay(self, channel, delay):
        self.write(DELAY, channel)
        self.writeInterval(delay, minf=100e-6)

    def setChannelM(self, channel, m):
        self.write(M, channel, m, ENTER, 0, ENTER)

    def setChannelVoltage(self, channel, voltage):
        assert(channel in self.channels)
        self.write(V, channel)
        self.writeVoltage(voltage, -12.7, 12.7, 1)

    def trigger(self, channel):
        assert(channel in self.channels)
        self.write(channel)

    def clearParadigm(self):
        self.write(OFF,ALL,ALL,ENTER)

    def copyParadigm(self, srcParadigm, destParadigm):
        assert(srcParadigm in self.paradigms)
        assert(destParadigm in self.paradigms)
        self.write(ALL, srcParadigm, destParadigm, ENTER)

    def connectChannel(self, srcChannel, triggeredChannel):
        assert(srcChannel in self.channels)
        assert(triggeredChannel in self.channels)
        self.write(CONNECT, srcChannel, triggeredChannel, ENTER)

    def disconnectChannel(self, srcChannel, triggeredChannel):
        assert(srcChannel in self.channels)
        assert(triggeredChannel in self.channels)
        self.write(DISCONNECT, srcChannel, triggeredChannel, ENTER)


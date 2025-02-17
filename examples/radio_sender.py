#!/usr/bin/env python3
import time
import sys
import serial
import argparse 

from serial.threaded import LineReader, ReaderThread

parser = argparse.ArgumentParser(description='LoRa Radio mode sender.')
parser.add_argument('port', help="Serial port descriptor")
args = parser.parse_args()

class PrintLines(LineReader):

    def connection_made(self, transport):
        print("connection made")
        self.transport = transport
        self.send_cmd("sys set pindig GPIO11 0")
        self.send_cmd('sys get ver')
        self.send_cmd('radio get mod')
        self.send_cmd('radio get freq')
        self.send_cmd('radio get sf')
        self.send_cmd('mac pause')
        self.send_cmd('radio set pwr 10')
        self.send_cmd("sys set pindig GPIO11 0")
        self.frame_count = 0

    def handle_line(self, data):
        if data == "ok":
            return
        print("RECV: %s" % data)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")

    def tx(self, val):
        self.send_cmd("sys set pindig GPIO11 1")
        #Convert to hexadecimal 
        # txmsg = 'radio tx %x%x' % (int(time.time()), self.frame_count)
        #Hexadecimal for 'hello'
        # txmsg = 'radio tx 68656c6c6f'
        val = str(val)
        val = val.encode('hex')
        txmsg = 'radio tx %s' % val
        self.send_cmd(txmsg)
        time.sleep(.3)
        self.send_cmd("sys set pindig GPIO11 0")
        self.frame_count = self.frame_count + 1

    def send_cmd(self, cmd, delay=.5):
        print("SEND: %s" % cmd)
        self.write_line(cmd)
        time.sleep(delay)


ser = serial.Serial(args.port, baudrate=57600)
with ReaderThread(ser, PrintLines) as protocol:
    val = 0
    while(1):
        val +=1
        protocol.tx(val)
        time.sleep(0.1)

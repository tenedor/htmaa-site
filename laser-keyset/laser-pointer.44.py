import Tkinter as Tk
import serial
import time
import random
import sys


events = {
    "mousedown": "<Button-1>",
    "mouseup": "<ButtonRelease-1>",
    "mousedrag": "<B1-Motion>",
    "mousemove": "<Motion>",
    "keypress": "<Key>",
}

keys = {
    "ESC": "\x1b",
    "DEL": "\x7f",
    "ENTER": "\r",
}


class Laser_Toggle_App:

    def __init__(self, master, ser):
        self.master_frame = master
        self.serial = ser

        master.bind_all(events["keypress"], self.on_keypress_global)

        canvas = self.canvas = Tk.Canvas(master, width=400, height=100,
                background='white')

        self.button_rects = []
        self.button_rects.append(canvas.create_rectangle(20, 20, 80, 80,
                fill='gray'))
        self.button_rects.append(canvas.create_rectangle(120, 20, 180, 80,
                fill='gray'))
        self.button_rects.append(canvas.create_rectangle(220, 20, 280, 80,
                fill='gray'))

        self.laser_rect = canvas.create_rectangle(320, 20, 380, 80, fill='gray')

        canvas.pack()

        self.read_serial_every_n_milliseconds(100)

    def on_keypress_global(self, e):
        c = e.char
        if c == 'q':
            self.master_frame.quit()

    def read_serial_every_n_milliseconds(self, ms):
        while self.serial.inWaiting() > 0:
            message = ord(self.serial.read())
            laser_on = bool(message & 1 << 3)
            button_states = message & 7

            if laser_on:
                self.canvas.itemconfigure(self.laser_rect, fill="red")
            else:
                self.canvas.itemconfigure(self.laser_rect, fill="gray")

            for i in range(3):
                if button_states & 1 << i:
                    self.canvas.itemconfigure(self.button_rects[i], fill="blue")
                else:
                    self.canvas.itemconfigure(self.button_rects[i], fill="gray")
        self.master_frame.after(ms, self.read_serial_every_n_milliseconds, ms)


#  check command line arguments
if (len(sys.argv) != 2):
    print "command line: ftdi-mosfets.44.py serial_port"
    sys.exit()
port = sys.argv[1]

# open serial port
ser = serial.Serial(port, 9600)
ser.setDTR()
ser.flush()

root = Tk.Tk()
root.title('ftdi-mosfets.44.py (q to exit)')

laser_toggle_app = Laser_Toggle_App(root, ser)

root.mainloop()

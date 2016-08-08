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

        # buttons

        buttons_frame = Tk.Frame(master)
        buttons_frame.pack(side=Tk.LEFT)

        on_btn = Tk.Button(buttons_frame, text="On", command=self.set_laser_on)
        on_btn.pack()

        off_btn = Tk.Button(buttons_frame, text="Off",
                command=self.set_laser_off)
        off_btn.pack()

        # board output

        self.output_field = output_field = Tk.Entry(master)
        output_field.pack(side=Tk.LEFT)

        self.read_serial_every_n_milliseconds(100)

    def set_output_field_to_value(self, value):
        self.output_field.delete(0, Tk.END)
        self.output_field.insert(0, str(value))

    def set_laser_on(self):
        self.serial.write('a');

    def set_laser_off(self):
        self.serial.write('b');

    def on_keypress_global(self, e):
        c = e.char
        if c == 'q':
            self.master_frame.quit()

    def read_serial_every_n_milliseconds(self, ms):
        while self.serial.inWaiting() > 0:
            chars = self.serial.read()
            print chars
            stmt = "board says: " + str(chars)
            self.set_output_field_to_value(stmt)
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

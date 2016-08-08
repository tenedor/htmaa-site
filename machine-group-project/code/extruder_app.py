import Tkinter as Tk


canvas_width = 660
canvas_height = 660
canvas_color = "#333"
line_color = "#fff"
thickness_options = range(1, 10 + 1) # [1, 2, ..., 10]
xyz_increment = 0.1
xyz_precision = 1 # number of decimal places of precision

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

draw_modes = {
    "line": "line",
    "scribble": "scribble",
}

keypress_no_propagate_list = []


class Drawing_App:

    def __init__(self, master):
        self.master_frame = master

        master.bind_all(events["keypress"], self.on_keypress_global)

        drawing_frame = Tk.Frame(master)
        drawing_frame.pack(side=Tk.LEFT)
        self.draw_drawing_ui(drawing_frame)

        machine_ui_frame = Tk.Frame(master)
        machine_ui_frame.pack(side=Tk.LEFT)
        self.draw_machine_ui(machine_ui_frame)


    # Drawing UI
    # ----------

    def draw_drawing_ui(self, container):
        self.draw_mode = draw_modes["line"]
        self.is_drawing = False
        self.drawing_list = []
        self.active_drawing = None
        self.draw_start = (None, None)
        self.mouse_pos = (None, None)
        self.thickness_index = 0

        buttons_frame = Tk.Frame(container)
        buttons_frame.pack()
        self.draw_drawing_buttons_ui(buttons_frame)

        thickness_frame = Tk.Frame(container)
        thickness_frame.pack()
        self.draw_thickness_ui(thickness_frame)

        output_frame = Tk.Frame(container)
        output_frame.pack()
        self.draw_output_ui(output_frame)

        self.draw_canvas(container)

    def draw_drawing_buttons_ui(self, container):
        line_btn = Tk.Button(container, text="Line", command=self.set_line_mode)
        line_btn.pack(side=Tk.LEFT)

        scribble_btn = Tk.Button(container, text="Scribble",
                command=self.set_scribble_mode)
        scribble_btn.pack(side=Tk.LEFT)

        del_btn = Tk.Button(container, text="Del",
                command=self.delete_last_drawing)
        del_btn.pack(side=Tk.LEFT)

        clear_btn = Tk.Button(container, text="Clear",
                command=self.clear_drawings)
        clear_btn.pack(side=Tk.LEFT)

        quit_btn = Tk.Button(container, text="Quit", command=self.quit)
        quit_btn.pack(side=Tk.LEFT)

    def draw_thickness_ui(self, container):
        tm_btn = Tk.Button(container, text="-", command=self.thickness_minus)
        tm_btn.pack(side=Tk.LEFT)

        tp_btn = Tk.Button(container, text="+", command=self.thickness_plus)
        tp_btn.pack(side=Tk.LEFT)

        self.thickness_value = thickness_value = Tk.StringVar()
        self.update_thickness_value()

        thickness_text = Tk.Label(container, textvariable=thickness_value)
        thickness_text.pack(side=Tk.LEFT)

    def draw_output_ui(self, container):
        self.output_field = output_field = Tk.Entry(container)
        output_field.pack()
        output_field.bind(events["keypress"], self.on_keypress_output_field)
        keypress_no_propagate_list.append(output_field)

        self.update_output_field()

    def draw_canvas(self, container):
        self.canvas = canvas = Tk.Canvas(container, width=canvas_width,
                height=canvas_height, bg=canvas_color)
        canvas.pack()

        canvas.bind(events["mousedown"], self.on_mousedown_canvas)
        canvas.bind(events["mousemove"], self.on_mousemove_canvas)


    # Machine UI
    # ----------

    def draw_machine_ui(self, container):
        xyz_selector_frame = Tk.Frame(container)
        xyz_selector_frame.pack()
        self.draw_xyz_selector_ui(xyz_selector_frame)

        messaging_frame = Tk.Frame(container)
        messaging_frame.pack()
        self.draw_machine_messaging_ui(messaging_frame)

    def draw_xyz_selector_ui(self, container):
        self.position = {'x': 0, 'y': 0, 'z': 0}

        x_frame = Tk.Frame(container)
        x_frame.pack()

        xm_btn = Tk.Button(x_frame, text="-x", command=self.x_minus)
        xm_btn.pack(side=Tk.LEFT)

        xp_btn = Tk.Button(x_frame, text="+x", command=self.x_plus)
        xp_btn.pack(side=Tk.LEFT)

        self.x_field = x_field = Tk.Entry(x_frame)
        x_field.pack(side=Tk.LEFT)
        x_field.bind(events["keypress"], self.on_keypress_x_field)
        keypress_no_propagate_list.append(x_field)

        y_frame = Tk.Frame(container)
        y_frame.pack()

        ym_btn = Tk.Button(y_frame, text="-y", command=self.y_minus)
        ym_btn.pack(side=Tk.LEFT)

        yp_btn = Tk.Button(y_frame, text="+y", command=self.y_plus)
        yp_btn.pack(side=Tk.LEFT)

        self.y_field = y_field = Tk.Entry(y_frame)
        y_field.pack(side=Tk.LEFT)
        y_field.bind(events["keypress"], self.on_keypress_y_field)
        keypress_no_propagate_list.append(y_field)

        z_frame = Tk.Frame(container)
        z_frame.pack()

        zm_btn = Tk.Button(z_frame, text="-z", command=self.z_minus)
        zm_btn.pack(side=Tk.LEFT)

        zp_btn = Tk.Button(z_frame, text="+z", command=self.z_plus)
        zp_btn.pack(side=Tk.LEFT)

        self.z_field = z_field = Tk.Entry(z_frame)
        z_field.pack(side=Tk.LEFT)
        z_field.bind(events["keypress"], self.on_keypress_z_field)
        keypress_no_propagate_list.append(z_field)

        self.reset_all_xyz_field_values()

    def draw_machine_messaging_ui(self, container):
        zero_btn = Tk.Button(container, text="Zero", command=self.zero_position)
        zero_btn.pack(side=Tk.LEFT)

        move_btn = Tk.Button(container, text="Move", command=self.move_machine)
        move_btn.pack(side=Tk.LEFT)

        send_btn = Tk.Button(container, text="Send",
                command=self.send_toolpath_to_machine)
        send_btn.pack(side=Tk.LEFT)


    # Drawing: General
    # ----------------

    def begin_drawing(self):
        self.is_drawing = True
        self.draw_start = self.mouse_pos
        self.update_active_drawing()

    def update_active_drawing(self):
        if not self.is_drawing:
            return

        self.update_drawing()

    def abort_drawing(self):
        if not self.is_drawing:
            return

        if self.active_drawing:
            self.delete_drawing(self.active_drawing)

        self.is_drawing = False
        self.active_drawing = None

    def complete_drawing(self):
        self.drawing_list.append(self.active_drawing)
        self.is_drawing = False
        self.active_drawing = None
        self.update_output_field()

    def delete_last_drawing(self):
        if self.is_drawing:
            self.abort_drawing()
        else:
            drawing = self.drawing_list.pop()
            self.delete_drawing(drawing)
            self.update_output_field()

    def clear_drawings(self):
        while len(self.drawing_list) > 0:
            self.delete_last_drawing()

    def thickness(self):
        return thickness_options[self.thickness_index]

    def update_thickness_value(self):
        self.thickness_value.set("Thickness: %s" % str(self.thickness()))

    def thickness_minus(self):
        self.thickness_index = max(self.thickness_index - 1, 0)
        self.update_thickness_value()

    def thickness_plus(self):
        max_index = len(thickness_options) - 1
        self.thickness_index = min(self.thickness_index + 1, max_index)
        self.update_thickness_value()

    def drawing_width_for_thickness(self, thickness):
        return 3 + thickness


    # Drawing: Modes
    # --------------

    # Multiplexer

    def update_drawing(self):
        draw_mode = self.draw_mode
        if draw_mode == draw_modes["line"]:
            self.update_line()
        elif draw_mode == draw_modes["scribble"]:
            self.update_scribble()

    def delete_drawing(self, drawing):
        draw_mode = drawing[0]["draw_mode"]
        if draw_mode == draw_modes["line"]:
            self.delete_line(drawing)
        elif draw_mode == draw_modes["scribble"]:
            self.delete_scribble(drawing)

    def printable_drawing(self, drawing):
        draw_mode = drawing[0]["draw_mode"]
        if draw_mode == draw_modes["line"]:
            return self.printable_line(drawing)
        elif draw_mode == draw_modes["scribble"]:
            return self.printable_scribble(drawing)

    # Line

    def set_line_mode(self):
        self.draw_mode = draw_modes["line"]

    def update_line(self):
        (x0, y0) = self.draw_start
        (x1, y1) = self.mouse_pos

        if self.active_drawing:
            self.canvas.coords(self.active_drawing[1], x0, y0, x1, y1)
        else:
            meta_data = {
                "draw_mode": draw_modes["line"],
                "thickness": self.thickness(),
            }
            width = self.drawing_width_for_thickness(meta_data["thickness"])
            line = self.canvas.create_line(x0, y0, x1, y1, fill=line_color,
                    width=width)
            self.active_drawing = [meta_data, line]

    def delete_line(self, drawing):
        self.canvas.delete(drawing[1])

    def printable_line(self, drawing):
        return [drawing[0], self.canvas.coords(drawing[1])]


    # Scribble

    def set_scribble_mode(self):
        self.draw_mode = draw_modes["scribble"]

    def update_scribble(self):
        (x1, y1) = self.mouse_pos

        if self.active_drawing:
            thickness = self.active_drawing[0]["thickness"]
            width = self.drawing_width_for_thickness(thickness)
            (_, _, x0, y0) = self.canvas.coords(self.active_drawing[-1])
            line = self.canvas.create_line(x0, y0, x1, y1, fill=line_color,
                    width=width)
            self.active_drawing.append(line)
        else:
            (x0, y0) = self.draw_start
            meta_data = {
                "draw_mode": draw_modes["scribble"],
                "thickness": self.thickness(),
            }
            width = self.drawing_width_for_thickness(meta_data["thickness"])
            line = self.canvas.create_line(x0, y0, x1, y1, fill=line_color,
                    width=width)
            self.active_drawing = [meta_data, line]

    def delete_scribble(self, drawing):
        [self.canvas.delete(d) for d in drawing[1:]]

    def printable_scribble(self, drawing):
        return [drawing[0]] + [self.canvas.coords(d) for d in drawing[1:]]


    # Machine: Commands
    # -----------------

    def zero_position(self):
        for axis in ['x', 'y', 'z']:
            self.position[axis] = 0
        self.reset_all_xyz_field_values()

    def move_machine(self):
        # first, update the UI to reflect the stored xyz values
        self.reset_all_xyz_field_values()

        # insert machine interfacing code here
        pass

    def send_toolpath_to_machine(self):
        # insert machine interfacing code here
        pass


    # Machine: Positioning UI
    # -----------------------

    def xyz_field_for_axis(self, axis):
        return {'x': self.x_field, 'y': self.y_field, 'z': self.z_field}[axis]

    def reset_xyz_field_value(self, axis):
        field = self.xyz_field_for_axis(axis)
        self.set_field_to_float_value(field, self.position[axis])

    def reset_all_xyz_field_values(self):
        for axis in ['x', 'y', 'z']:
            self.reset_xyz_field_value(axis)

    def increment_xyz(self, axis, increment):
        self.position[axis] += increment
        field = self.xyz_field_for_axis(axis)
        self.set_field_to_float_value(field, self.position[axis])

    def x_minus(self): self.increment_xyz('x', -xyz_increment)
    def x_plus(self):  self.increment_xyz('x',  xyz_increment)
    def y_minus(self): self.increment_xyz('y', -xyz_increment)
    def y_plus(self):  self.increment_xyz('y',  xyz_increment)
    def z_minus(self): self.increment_xyz('z', -xyz_increment)
    def z_plus(self):  self.increment_xyz('z',  xyz_increment)


    # Utilities
    # ---------

    def focus_clear(self):
        self.master_frame.focus_set()

    def set_field_to_value(self, field, value):
        field.delete(0, Tk.END)
        field.insert(0, value)

    def set_field_to_float_value(self, field, value, precision=xyz_precision):
        self.set_field_to_value(field, ("%." + str(precision) + "f") % value)

    def update_output_field(self):
        self.set_field_to_value(self.output_field, str(self.toolpath()))

    def toolpath_for_drawing(self, drawing):
        printable_drawing = self.printable_drawing(drawing)
        meta_data = printable_drawing[0]
        lines = printable_drawing[1:]
        mode = meta_data["draw_mode"]
        thickness = meta_data["thickness"]

        if mode == draw_modes["line"]:
            line = lines[0]
            points = [line[0:2], line[2:4]]
            return [thickness, points]

        elif mode == draw_modes["scribble"]:
            points = [pt for line in lines for pt in [line[0:2], line[2:4]]]
            unique_points = [points[0]]
            for pt in points[1:]:
                if pt != unique_points[-1]:
                    unique_points.append(pt)
            return [thickness, unique_points]

    def toolpath(self):
        return [self.toolpath_for_drawing(d) for d in self.drawing_list]

    def quit(self):
        print self.toolpath()
        self.master_frame.quit()


    # Events
    # ------

    def on_mousedown_canvas(self, e):
        self.focus_clear()
        self.mouse_pos = (e.x, e.y)
        if self.is_drawing:
            self.complete_drawing()
        else:
            self.begin_drawing()

    def on_mousemove_canvas(self, e):
        self.mouse_pos = (e.x, e.y)
        self.update_active_drawing()

    def on_keypress_global(self, e):
        if e.widget in keypress_no_propagate_list:
            return
        c = e.char
        if c == keys['ESC']:
            self.abort_drawing()
        elif c in [keys['DEL'], 'u']:
            self.delete_last_drawing()
        elif c == 'c':
            self.clear_drawings()
        elif c == 'q':
            self.quit()
        elif c == '1':
            self.set_line_mode()
        elif c == '2':
            self.set_scribble_mode()
        elif c == '-':
            self.thickness_minus()
        elif c in ['+', '=']:
            self.thickness_plus()

    def on_keypress_output_field(self, e):
        c = e.char
        if c == keys['ESC']:
            self.focus_clear()

    def on_keypress_x_field(self, e): self.on_keypress_xyz_field(e, 'x')
    def on_keypress_y_field(self, e): self.on_keypress_xyz_field(e, 'y')
    def on_keypress_z_field(self, e): self.on_keypress_xyz_field(e, 'z')

    def on_keypress_xyz_field(self, e, axis):
        field = self.xyz_field_for_axis(axis)
        value = field.get()

        c = e.char

        if c == keys['ESC']:
            self.reset_xyz_field_value(axis)
            self.focus_clear()

        elif c == keys['ENTER']:
            try:
                float_value = float(value)
                self.position[axis] = float_value
            except ValueError:
                print "Error: invalid value passed to %c field" % axis


root = Tk.Tk()

drawing_app = Drawing_App(root)

root.mainloop()

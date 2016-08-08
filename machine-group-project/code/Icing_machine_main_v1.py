# Harvard Section 2015 MTM project
# Icing_machine_main_v1.py - Main module, ties together other peoples' code

import Harvard15_gestaltcode_v1_0 as gestalt #contains machine definition stuff based on Nadya's code
#import mas863h_15_gui as gui #When gui is fully implemented by Daniel
#import mas863h_15_drawing_to_instructions as drawing_decoder #When Jeffery fully completes transfer function/drawing decoder
import time
import io
import sys

# MAIN STUFF

# load machine from local persistence file
stages = gestalt.virtualMachine(persistenceFile="icing_machine.vmp")

#Load the GUI, in order to be ready for drawing and stuff
# local_gui = gui.init_gui() 

# define the speed for the axes
stages.xabyzNode.setVelocityRequest(8)

# Define the zeroes for the three axes
local_zeroes = [0, 0, 0]
current_coords = local_zeroes


def event_loop():
    # local_gui.update() # update and sample inputs
    # gui_status = local_gui.get_status()
    # if (gui_status == gui.status_jog_xplus): # If we want to implement moving manually as jogging (hold down button to move)
        # current_coords[0] += jog_distance
        # move(current_coords)
    # Et cetera on the other jog directions--better method would be appreciated
    # elif (gui_status == gui.status_move): # If we want to implement moving manually as type in x, y, z
        # move (local_gui.move_coords, check_for_stop) # Move to the new point, checking for a stop every time
    # elif (gui_status == gui.status_set_zeroes):
        # local_zeroes = current_coords
    # elif (gui_status == gui.status_send_instructions):
        # for next_point in drawing_decoder.decode(local_gui.get_full_path()):
            # stages.extruder(next_point[3]) # turn on the extruder iff it's supposed to be on
            # move(next_point[0:3], wait_function = check_for_stop()) # Split the xyz coordinates off to move the 
        

# Move to the point in *coords.  Call wait_function in loop
def move(*coords, wait_function = None):
    move = [coords[0], coords[0], coords[1], coords[2]]
    # use the x,y coordinates stored in the 'move' list in the 'move' function
    stages.move(move, 0)
    
    # Poll the status
    status = stages.xaAxisNode.spinStatusRequest()
    # This checks to see if the move is done.
    while status['stepsRemaining'] > 0:
        time.sleep(0.001)
        status = stages.xaAxisNode.spinStatusRequest()
        wait_function

def check_for_stop():
    # local_gui.update() # update and sample inputs
    # gui_status = local_gui.get_status()
    # if (gui_status == gui.status_pause):
        # No idea how to store the data, or break out of the loop
        # stages.extruder(0) # tun off extruder
    # elif (gui_status == gui.status_cancel):
        # Also don't know how to force the axes to stop
        # stages.extruder(0) # Turn off extruder
        
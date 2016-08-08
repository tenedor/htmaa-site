# HTM Harvard Section 2015
# Icing extruder project gestalt node code
# Tiffany Cheng, Brendan Bogorzmir, Jeffery Durand, Daniel Windham, and Ben Garber

#------IMPORTS-------
from pygestalt import nodes
from pygestalt import interfaces
from pygestalt import machines
from pygestalt import functions
from pygestalt.machines import elements
from pygestalt.machines import kinematics
from pygestalt.machines import state
from pygestalt.utilities import notice
from pygestalt.publish import rpc  # remote procedure call dispatcher
import time
import io
import sys


#------VIRTUAL MACHINE------
class virtualMachine(machines.virtualMachine):

    def initInterfaces(self):
        if self.providedInterface:
            # providedInterface is defined in the virtualMachine class.
            self.fabnet = self.providedInterface
        else:
		    self.fabnet = interfaces.gestaltInterface('FABNET', interfaces.serialInterface(baudRate = 115200, interfaceType = 'ftdi', portName = '/dev/tty.usbserial-FTXYJGOO'))

    def initControllers(self):
        self.xaAxisNode = nodes.networkedGestaltNode(
            'XA Axis', self.fabnet, filename='086-005a.py', persistence=self.persistence)
        self.xbAxisNode = nodes.networkedGestaltNode(
            'XB Axis', self.fabnet, filename='086-005a.py', persistence=self.persistence)
        self.yAxisNode = nodes.networkedGestaltNode(
            'Y Axis', self.fabnet, filename='086-005a.py', persistence=self.persistence)
        self.zAxisNode = nodes.networkedGestaltNode(
            'Z Axis', self.fabnet, filename='086-005a.py', persistence=self.persistence)
        self.extruderNode = nodes.networkedGestaltNode(
            'Extruder', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
        self.xabyzNode = nodes.compoundNode(
            self.xaAxisNode, self.xbAxisNode, self.yAxisNode, self.zAxisNode)

    def initCoordinates(self):
        self.position = state.coordinate(['mm', 'mm', 'mm', 'mm'])

    def initKinematics(self):
        self.xaAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), 
                                                    elements.leadscrew.forward(8), elements.invert.forward(False)])
        self.xbAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), 
                                                     elements.leadscrew.forward(8), elements.invert.forward(False)])  
        self.yAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), 
                                                    elements.leadscrew.forward(8), elements.invert.forward(False)])
        self.zAxis = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8), 
                                                    elements.leadscrew.forward(8), elements.invert.forward(False)])
        self.extruder = elements.elementChain.forward([elements.microstep.forward(4), elements.stepper.forward(1.8),
                                                       elements.leadscrew.forward(8), elements.invert.forward(False)])
        self.stageKinematics = kinematics.direct(4)  # direct drive on all axes
        self.extruderKinematics = kinematics.direct(1) # direct drive on extruder (though frankly I want velocity control, not position control)

    def initFunctions(self):
        self.move = functions.move(virtualMachine=self, virtualNode=self.xabyzNode, 
                                   axes=[self.xaAxis, self.xbAxis, self.yAxis, self.zAxis], 
                                   kinematics=self.stageKinematics, machinePosition=self.position, planner='null')
        # an incremental wrapper for the move function
        self.jog = functions.jog(self.move)
        pass

    def initLast(self):
        #self.machineControl.setMotorCurrents(aCurrent = 0.8, bCurrent = 0.8, cCurrent = 0.8)
        # self.xNode.setVelocityRequest(0)   #clear velocity on nodes.
        # Eventually this will be put in the motion planner on initialization
        # to match state.
        pass

    def publish(self):
        # self.publisher.addNodes(self.machineControl)
        pass

    def getPosition(self):
        return {'position': self.position.future()}

    def setPosition(self, position=[None]):
        self.position.future.set(position)

    def setSpindleSpeed(self, speedFraction):
        # self.machineControl.pwmRequest(speedFraction)
        pass

#------IF RUN DIRECTLY FROM TERMINAL------
if __name__ == '__main__':
    # The persistence file remembers the node you set. It'll generate the first time you run the
    # file. If you are hooking up a new node, delete the previous persistence
    # file.
    stages = virtualMachine(persistenceFile="test.vmp")

    # You can load a new program onto the nodes if you are so inclined. This is currently set to
    # the path to the 086-005 repository on Nadya's machine.
    # stages.xyNode.loadProgram('../../../086-005/086-005a.hex')

    # This is a widget for setting the potentiometer to set the motor current limit on the nodes.
    # The A4982 has max 2A of current, running the widget will interactively help you set.
    # stages.xyNode.setMotorCurrent(0.7)

    # This is for how fast the
    stages.xabyzNode.setVelocityRequest(8)
    txt_path = "path.txt"
    if len(sys.argv) > 1:
        txt_path = sys.argv[1]
    text_file = open(txt_path, "r")
    lines = text_file.readline()  # this stores each lines in a string list
    for lines in text_file:
        # seperate coordinates that are seperated by comas and store them in
        # the chars list
        chars = lines.split(',')
        # send the first and second char to the 'move' list
        if len(chars) == 2:
            move = [chars[0], chars[0], chars[1], 0]
        else:
            move = [chars[0], chars[0], chars[1], chars[2]]
        # use the x,y coordinates stored in the 'move' list in the 'move'
        # function
        stages.move(move,0)
        status = stages.xaAxisNode.spinStatusRequest()
        # This checks to see if the move is done.
        while status['stepsRemaining'] > 0:
            time.sleep(0.001)
            status = stages.xaAxisNode.spinStatusRequest()
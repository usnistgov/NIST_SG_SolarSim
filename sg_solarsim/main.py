""" Solar Sim main program
    Launches ss_gui
    closes when ss_gui is closed
"""
from sg_solarsim.ss_gui import SSTopGui

sstop = SSTopGui()
sstop.start_gui()

while 1:
    # first check to see if the gui has been closed
    if sstop.state == 'CLOSED':
        break

    # This is the "outer loop"
    # if the TMY Clock is running, update it
    sstop.run_gui()

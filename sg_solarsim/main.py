""" Solar Sim main program
    Launches ss_gui
    closes when ss_gui is closed
"""
from sg_solarsim.ss_gui import SSTopGui

def main(plt_curve=False):
    """
    Starts the solarsim gui and runs it in a while loop

    :param plt_curve: boolean if True will plot the I-V curve while the tmy clock is running
    :return: none
    """

    sstop = SSTopGui(modlistname='CECMod', iv_plot=True)
    sstop.start_gui()

    #
    #module_info = sstop.get_module_info()
    #module_params = sstop.modules[module_info['type']]
    #print(module_params)

    while 1:
        # first check to see if the gui has been closed
        if sstop.state == 'CLOSED':
            break

        # This is the "outer loop"
        # if the TMY Clock is running, update it
        sstop.run_gui()

        #check for change in the UI to the solar array
        # temp = sstop.get_module_info()
        # if temp != module_info:
        #     module_info = temp
        #     module_params = sstop.modules[module_info['type']]
        #     #print(module_params)


        # if sstop.clk != []:     # the clock is instantiated
        #     # adjust the reference parameters according to the operating
        #     # conditions using the DeSoto model
        #     Il, I0, Rs, Rsh, nNsVth = sstop.calcparams_desoto()
        #
        #     if plt_curve:
        #         # Plug the parameters into the Single Diode Equation and solve
        #         curve_info = sstop.singleDiode(Il, I0, Rs, Rsh, nNsVth)
        #         update_plt(curve_info, ax)


if __name__ == "__main__":
    main(plt_curve=True)

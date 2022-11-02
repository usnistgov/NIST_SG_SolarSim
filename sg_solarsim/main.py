""" Solar Sim main program
    Launches ss_gui
    closes when ss_gui is closed
"""
from sg_solarsim.ss_gui import SSTopGui
from mppt import MPPT

import matplotlib.pyplot as plt


def main(plt_curve=False):
    """
    Starts the solarsim gui and runs it in a while loop

    :param iv_plot: boolean if True will plot the I-V curve while the tmy clock is running
    :return: none
    """

    sstop = SSTopGui(modlistname='CECMod', iv_plot=True)
    sstop.start_gui()

    # instantiate an mppt tracker with default values
    mppt = MPPT()
    v_ref = mppt.v_ref

    # figure to plot the mppt tracker
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xbound(45)
    ax.set_ybound(10)
    fig.show()


    while 1:
        # first check to see if the gui has been closed
        if sstop.state == 'CLOSED':
            break

        # This is the "outer loop"
        # if the TMY Clock is running, update it
        sstop.run_gui()


        if sstop.clk != []:
            # get the module current at the present v_ref
            IL, I0, Rs, Rsh, nNsVth = sstop.calcparams_desoto(g_eff=sstop.clk.g_eff, t_eff=sstop.clk.t_air)
            current = sstop.i_from_v(Rsh, Rs, nNsVth, v_ref, I0, IL)

            # run the mppt algorithm to get the new v_ref then get the new current
            v_ref = mppt.inc_cond(v_ref, current)
            current = sstop.i_from_v(Rsh, Rs, nNsVth, v_ref, I0, IL)

            # plot the new v-i point
            #print (v_ref, current)
            ax.plot(v_ref, current, marker='o')
            fig.show()


if __name__ == "__main__":
    main(plt_curve=True)

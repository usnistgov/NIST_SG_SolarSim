"""ss_gui module:  Graphical User Interface for the NIST Solar Array Simulator python code"""

# standard library imports

# third party imports
# pvlib-python
import PySimpleGUI as sg
import pvlib.pvsystem as pvsys
from pvlib.location import Location

from datetime import datetime, timedelta

import pandas as pd
import matplotlib.pyplot as plt

# package resources
from pkg_resources import resource_stream, resource_filename

# local modules and classes
from sg_solarsim.tmy_clock import tmy_clock


class SSTopGui:
    """ Top level GUI for the Solar Array Simulator Python code"""

    def __init__(self, modlistname='SandiaMod', theme='Dark Grey 8', iv_plot=False):
        """
        :param modlistname: The name of the module list to get module data from.
                            Must match of the module lists in the pvlib-python data folder
        :type modlistname: string
        :param theme: color theme for the PySimpleGui window
        :type theme: string
        :param iv_plot: create a plot for the i-v curve
        :type iv_plot: boolean
        """

        self.modules = pvsys.retrieve_sam(modlistname)
        module_names = self.modules.columns.values.tolist()
        combo_modules = sg.DD(module_names,
                              default_value=module_names[0],
                              key='-MODULES-',
                              enable_events=True)    # Modules drop down
        self.theme = sg.theme(theme)
#        tbar = sg.Titlebar(title='PV IV Curve',
#                           icon=resource_filename('sg_solarsim.resources.images','GS-PV-array-icon.png'),
#                           )
        self.window = []    # placeholder for the gui window object
        self.clk = []       # placeholder for the TMY_Clock object
        self.state = "OPEN"

        # cityPicker object
        self.cp = CityPicker()

        today = datetime.today().strftime('%B %d')
        tomorrow = (datetime.today()+timedelta(1)).strftime('%B %d')

        button_images = [resource_filename('sg_solarsim.resources.images', 'play.png'), resource_filename('sg_solarsim.resources.images','pause.png'),resource_filename('sg_solarsim.resources.images','stop.png')]

        self.layout = [
            #[tbar],
            [sg.Text('Solar Modules')],
            [sg.Text('Series'), sg.Spin(values=[i for i in range(1,10)], key='-SERIES-', initial_value=1), sg.Text('Parallel'), sg.Spin(values=[i for i in range(1,10)], key='-PARALLEL-', initial_value=1)],
            [combo_modules],
            [sg.Text('Location')],
            [[self.cp.ddCountry, self.cp.ddCity]],
            [[sg.Text('latitude'), self.cp.txt_lat, sg.Text('longitude'), self.cp.txt_lng]],
            [sg.Input(today, key='-START-', size=(14, 1), disabled=True, disabled_readonly_background_color='', justification='center'), sg.Input(tomorrow, key='-END-', size=(14,1), disabled=True, disabled_readonly_background_color='', justification='center')],
            [sg.CalendarButton('Start Date', close_when_date_chosen=True, target='-START-', no_titlebar=True, format='%B %d'), sg.CalendarButton('End Date', close_when_date_chosen=True, target='-END-', no_titlebar=True, format='%B %d')],
            [sg.Slider(range=(0,15),orientation='h', disable_number_display=True,enable_events=True, key='-SLIDER-'),sg.Text('Speed x'),sg.Input(1, key='-SPEED-',size=(4,1), disabled=True, disabled_readonly_background_color='')],
            [sg.Button(image_filename=button_images[0], image_subsample=5, key='-PLAY-', disabled=False), sg.Button(image_filename=button_images[1], image_subsample=5, key='-PAUSE-', disabled=True), sg.Button(image_filename=button_images[2], image_subsample=5, key='-STOP-', disabled=True)],
            [sg.Cancel("Close")]
        ]
        # will there be a plot for the i-v curve?
        self.iv_plot = iv_plot
        self.fig = None
        self.ax = None
        self.line = None
        if self.iv_plot:
            self.fig, self.ax = plt.subplots()


    def launch_clock(self):
        """ launched the TMY Clock window"""
        if self.clk == []:
            starttime = datetime.strptime(self.window.Element('-START-').get(), '%B %d')
            endtime = datetime.strptime(self.window.Element('-END-').get(), '%B %d')
            self.clk = tmy_clock(speed=int(self.window.Element("-SPEED-").get()), starttime=starttime, endtime=endtime, nosecond=False)
            if self.iv_plot:
                # plot a default i-v curve
                IL, I0, Rs, Rsh, nNsVth = self.calcparams_desoto(g_eff=1000, t_eff=self.clk.t_air)
                curve_info = self.singleDiode(IL, I0, Rs, Rsh, nNsVth)
                self.fig = plt.figure()
                self.ax = self.fig.add_subplot(111)
                self.line = self.ax.plot(curve_info['v'], curve_info['i'])
                self.fig.show()
        self.clk.pause = False


    def start_gui(self):
        self.window = sg.Window('NIST Solar Simulation', self.layout, element_justification='center', finalize=True)

    def run_gui(self):
        """ looks for element events """

        event, values = self.window.Read(timeout = 100)
        if event in (sg.WIN_CLOSED, 'Close'):
            self.window.close()
            self.state="CLOSED"
        if event == '-COUNTRY-':
            self.cp.countrychanged(values['-COUNTRY-'])
        if event == '-CITY-':
            self.cp.citychanged(values['-CITY-'])
        if event == '-SLIDER-':
            self.window.Element('-SPEED-').Update(2**int(values['-SLIDER-']))
            if type(self.clk) == tmy_clock:
                self.clk.speed = int(self.window.Element("-SPEED-").get())
        if event == '-PLAY-':
            self.window['-PLAY-'].update(disabled=True)
            self.window['-PAUSE-'].update(disabled=False)
            self.window['-STOP-'].update(disabled=False)
            self.launch_clock()
        if event == '-STOP-':
            self.window['-PLAY-'].update(disabled=False)
            self.window['-PAUSE-'].update(disabled=True)
            self.window['-STOP-'].update(disabled=True)
            self.clk.destroy()
            self.clk = []
            if self.iv_plot:
                plt.close(self.fig)
        if event == '-PAUSE-':
            self.window['-PLAY-'].update(disabled=False)
            self.window['-PAUSE-'].update(disabled=True)
            self.window['-STOP-'].update(disabled=False)
            self.clk.pause = True

        # if the clock is running
        if type(self.clk) == tmy_clock:
            self.clk.update()
            self.clk.update_idletasks()
            self.clk.update_class()

            # update the i-v curve if drawn
            if self.state != 'CLOSED':
                if self.iv_plot:
                    IL, I0, Rs, Rsh, nNsVth = self.calcparams_desoto(g_eff=self.clk.g_eff, t_eff=self.clk.t_air)
                    curve_info = self.singleDiode(IL, I0, Rs, Rsh, nNsVth)
                    self.line[0].set(xdata=curve_info['v'], ydata=curve_info['i'])
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()

    def get_module_info(self):
        return {'type': self.window.Element('-MODULES-').get(), 'series': self.window.Element('-SERIES-').get(), 'parallel': self.window.Element('-PARALLEL-').get(),}

    def calcparams_desoto(self, g_eff=500, t_eff=25, module_params=None):
        # adjust the reference parameters according to the operating
        # conditions using the DeSoto model

        if module_params == None:
            module_params = self.modules[self.get_module_info()['type']]

        IL, I0, Rs, Rsh, nNsVth = pvsys.calcparams_desoto(
             g_eff,
             t_eff,
             module_params['alpha_sc'],
             module_params['a_ref'],
             module_params['I_L_ref'],
             module_params['I_o_ref'],
             module_params['R_sh_ref'],
             module_params['R_s'],
             EgRef=1.121,
             dEgdT=-0.0002677
            )
        return IL, I0, Rs, Rsh, nNsVth


    def singleDiode(self, IL, I0, Rs, Rsh, nNsVth, pnts=100, method='lambertw'):
        curve_info = []
        if IL <= 0:
            IL = 0.001
        curve_info = pvsys.singlediode(
            photocurrent=IL,
            saturation_current=I0,
            resistance_series=Rs,
            resistance_shunt=Rsh,
            nNsVth=nNsVth,
            ivcurve_pnts=pnts,
            method=method
        )
        return curve_info

class CityPicker:
    """ A pair of drop down controls populated with country and city
        a pair of text boxes with the lat and long of the city
        choosing a country populates the city list
        choosing a city or country populates the text boxes with the location

    """

    def __init__(self, default_country='United States', default_city='Gaithersburg - Maryland'):
        """
        :param default_country:         Choice to be displayed as initial country value.
                                        Must match a country value from the worldcities.csv
        :type default_country:          string
        :param default_city:            Choice to be displayed as intital city value.
                                        Must match city_ascii - admin_name fields from corldcities.csv
        :type default_city:             string
        """
        worldcities_stream = resource_stream('sg_solarsim.resources.data','worldcities.csv')
        self.worldcities = pd.read_csv(worldcities_stream, usecols=['country', 'city_ascii', 'admin_name', 'lat', 'lng'])
        #self.worldcities = pd.read_csv('worldcities.csv', usecols=['country', 'city_ascii', 'admin_name', 'lat', 'lng'])
        self.worldcities = self.worldcities.sort_values(by=['country', 'city_ascii'])
        countrylist = self.worldcities['country'].drop_duplicates()
        self.ddCountry = sg.DD(countrylist.values.tolist(),
                               default_value='United States',
                               key='-COUNTRY-',
                               enable_events=True)
        citylist = self.worldcities.loc[self.worldcities['country'] == default_country]
        city_admin = citylist['city_ascii'] + ' - ' + citylist['admin_name']
        self.ddCity = sg.DD(city_admin.values.tolist(),
                            default_value=default_city,
                            key='-CITY-',
                            enable_events=True)

        # instantiate a pvlib location object
        self.loc = []
        self.update_loc(default_city)
        self.txt_lat = sg.Text(self.loc.latitude)
        self.txt_lng = sg.Text(self.loc.longitude)

    def countrychanged(self, key):
        """Called when the country combo box is changed by the user
            :param key
            :type  string
            """
        citylist = self.worldcities.loc[self.worldcities['country'] == key]
        city_admin = citylist['admin_name']
        if isinstance(city_admin.values[0],str): # some data entries have no admin_name
            city_admin = citylist['city_ascii'] + ' - ' + citylist['admin_name']
        else:
            city_admin = citylist['city_ascii'] + ' - ' + ""
        self.ddCity.update(values=city_admin.values.tolist(), set_to_index=0)
        self.update_loc(city_admin.values[0])
        self.txt_lat.update(self.loc.latitude)
        self.txt_lng.update(self.loc.longitude)

    def citychanged(self, key):
        """Called when the city combo box is changed by the user
             :param key
             :type  string
             """
        self.update_loc(key)
        self.txt_lat.update(self.loc.latitude)
        self.txt_lng.update(self.loc.longitude)

    def update_loc(self,key):
        """
            Update the location to the new location
        :param key:
        :return:
        """
        # latitude and longitude
        [city, state] = key.split(' - ')
        if state != '':    # some data entries have no admin_name
            row = self.worldcities[((self.worldcities['city_ascii'] == city) & (self.worldcities['admin_name'] == state))]
        else:
            row = self.worldcities[((self.worldcities['city_ascii'] == city))]
        lat = float(row['lat'].to_numpy()[0])
        lng = longitude = float(row['lng'].to_numpy()[0])
        self.loc = Location(latitude=lat, longitude=lng, name=city)





def main():
    sstop = SSTopGui()
    sstop.start_gui()
    while 1:
        if sstop.state == "CLOSED":
            break
        sstop.run_gui()


if __name__ == "__main__":
    main()

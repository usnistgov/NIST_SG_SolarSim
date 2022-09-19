"""ss_gui module:  Graphical User Interface for the NIST Solar Array Simulator python code"""

# standard library imports
import math

# third party imports
# pvlib-python
import PySimpleGUI as sg
import pvlib.pvsystem as pvsys
from pvlib.location import Location

from datetime import datetime, timedelta

import pandas as pd

# package resources
from pkg_resources import resource_stream, resource_filename

# local modules and classes
from tmy_clock import tmy_clock

class SSTopGui:
    """ Top level GUI for the Solar Array Simulator Python code"""

    def __init__(self, modlistname='SandiaMod', theme='Dark Grey 8'):
        """
        :param modlistname: The name of the module list to get module data from.
                            Must match of the module lists in the pvlib-python data folder
        :type modlistname: string
        :param theme: color theme for the PySimpleGui window
        :type theme: string
        """

        self.modules = pvsys.retrieve_sam(modlistname)
        module_names = self.modules.columns.values.tolist()
        combo_modules = sg.DD(module_names,
                              default_value='SunPower_SPR_220_BLK_U_Module___2008_',
                              key='-MODULES-',
                              enable_events=True)    # Modules drop down
        self.theme = sg.theme(theme)
        tbar = sg.Titlebar(title='PV IV Curve',
                           icon=resource_filename('sg_solarsim.resources.images','GS-PV-array-icon.png'),
                           )
        self.window = []    # placeholder for the gui window object
        self.clk = []       # placeholder for the TMY_Clock object
        self.state = "OPEN"

        # cityPicker object
        self.cp = CityPicker()

        today = datetime.today().strftime('%B %d')
        tomorrow = (datetime.today()+timedelta(1)).strftime('%B %d')

        button_images = [resource_filename('sg_solarsim.resources.images','play.png'),resource_filename('sg_solarsim.resources.images','pause.png'),resource_filename('sg_solarsim.resources.images','stop.png')]

        self.layout = [
            #[tbar],
            [sg.Text('Solar Module')],
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

    def launch_clock(self):
        """ launched the TMY Clock window"""
        if self.clk == []:
            starttime = datetime.strptime(self.window.Element('-START-').get(), '%B %d')
            endtime = datetime.strptime(self.window.Element('-END-').get(), '%B %d')
            self.clk = tmy_clock(speed=int(self.window.Element("-SPEED-").get()), starttime=starttime, endtime=endtime, nosecond=False)
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

"""TMY_Clock
Typical Meterological Year analog clock face
"""
import tkinter

try:
	import Tkinter
except:
	import tkinter as Tkinter

import math	# Required For Coordinates Calculation
from datetime import datetime, timedelta
from pytz import utc, timezone
from timezones import timezones

from pvlib import iotools

class tmy_clock(Tkinter.Tk):
    """"""
    def __init__(self, lat=39.13, lng=-77.21, speed=1, starttime=datetime.now(), endtime=datetime.now() + timedelta(weeks=2), nosecond=False):
        """

        :param speed:  Time multiplier
        :param starttime:  Datetime to start the clock
        :param endtime:   Datetime to pause the clock at the end of the run
        :param nosecond:  Bool to remove the second hand
        """
        Tkinter.Tk.__init__(self)
        self.x = 154    # Center point x
        self.y = 154    # center point y
        self.length = [100,125,125]  # stick length
        self.width = [4,2,1]
        self.color = 254
        self.speed = speed
        self.nosecond = nosecond
        self.then = []
        self.displaytime = []
        self.tz = timezone(timezones(lat, lng).tz)
        self.starttime = self.tz.localize(starttime.replace(year=2000))
        self.endtime = self.tz.localize(endtime.replace(year=2000))
        self.elapsed = timedelta()
        self.creating_all_function_trigger()
        self.title('TMY Clock')
        self.pause = False

        # get the tmy data
        self.tmy_slice = tmy(lat=lat, lng=lng, tz=self.tz, daterange=[self.starttime, self.endtime]).tmy_slice

        #self.iconphoto(False, Tkinter.PhotoImage(file='GS-PV-array-icon.png'))


    # Creating Trigger for other functions
    def creating_all_function_trigger(self):
        self.create_canvas_for_shapes()
        self.creating_background_()
        self.creating_sticks()
        self.creating_datelabel()
        return

    # creating canvas
    def create_canvas_for_shapes(self):
        #icon = Tkinter.PhotoImage(file='GS-PV-array-icon.png')
        #self.iconphoto(False,Tkinter.PhotoImage(file='GS-PV-array-icon.png'))
        self.canvas = Tkinter.Canvas(self, bg='blue', width=312, height=400)
        self.canvas.pack(expand='no',fill='both')
        return

    # creating background
    def creating_background_(self):
        self.clkface = self.canvas.create_oval(8,8,308,308,fill='gray50', outline='red', width=4)
        return

    # creating moving sticks
    def creating_sticks(self):
        self.sticks=[]
        if self.nosecond:
            self.length = self.length[0:2]
        for n,i in enumerate(self.length):
            store = self.canvas.create_line(self.x,self.y,self.x+i,self.y+n,width=self.width[n],fill='red')
            self.sticks.append(store)
        return

    def creating_datelabel(self):
        #self.datelabel = tkinter.Frame(self.canvas, bd=2, padx=20, pady=20)
        #tkinter.Label(self.datelabel,text = 'August 24')
        self.datelabel = tkinter.Label(self.canvas, text=self.starttime.strftime('%B %d'), bd=4, font=('Times', '24', 'bold'), bg='grey75', relief='ridge')
        self.canvas.create_window(156, 349, window=self.datelabel, anchor='center')
        return

    def update_class(self):
        now = datetime.now()
        if self.pause:
            self.then = now
        if self.displaytime == []:
            self.displaytime = self.starttime
        else:
            elapsed = now - self.then
            self.elapsed += elapsed * self.speed
            self.displaytime = self.starttime + self.elapsed

        self.then = now
        #t = time.strptime(str(self.displaytime.tm_hour), "%H")
        #hour = int(time.strftime('%I', t))*5
        hour = int(self.displaytime.strftime('%I')) * 5
        min = int(self.displaytime.strftime('%M'))
        sec = int(self.displaytime.strftime('%S'))
        now=(hour,min,sec)

        # changing the sticks coordinates continuously
        # Hour stick
        x, y = self.canvas.coords(self.sticks[0])[0:2]
        cr = [x,y]
        cr.append(self.length[0] * math.cos(math.radians((now[0] * 6) + (now[1] * 6) / 12) - math.radians(90)) + self.x)
        cr.append(self.length[0] * math.sin(math.radians((now[0] * 6) + (now[1] * 6) / 12) - math.radians(90)) + self.x)
        self.canvas.coords(self.sticks[0], tuple(cr))

        # minute stick
        x, y = self.canvas.coords(self.sticks[1])[0:2]
        cr = [x,y]
        cr.append(self.length[1] * math.cos(math.radians((now[1] * 6) + (now[2] * 6) / 60) - math.radians(90)) + self.x)
        cr.append(self.length[1] * math.sin(math.radians((now[1] * 6) + (now[2] * 6) / 60) - math.radians(90)) + self.x)
        self.canvas.coords(self.sticks[1], tuple(cr))

        # second stick
        if not self.nosecond:
            x, y = self.canvas.coords(self.sticks[2])[0:2]
            cr = [x, y]
            cr.append(self.length[2] * math.cos(math.radians((now[2] * 6)) - math.radians(90)) + self.x)
            cr.append(self.length[2] * math.sin(math.radians((now[2] * 6)) - math.radians(90)) + self.x)
            self.canvas.coords(self.sticks[2], tuple(cr))

        # Determine the face color based on a linear interpolation of the ghi data
        time = (self.displaytime.replace(minute=0, second=0, microsecond=0))
        tmy_rows = self.tmy_slice.loc[time : time + timedelta(hours=1)]
        seek = (self.displaytime.timestamp() % 3600) / 3600
        X, Y = self.interpolate(
            tmy_rows.index[0].timestamp(),
            tmy_rows.iloc[0]['ghi'],
            tmy_rows.index[1].timestamp(),
            tmy_rows.iloc[1]['ghi'],
            seek
        )

        self.change_color(int(round((Y/1000)*256)))

        # update the date
        txt = self.displaytime.strftime('%B %d')
        if self.pause:
            txt += ' (paused)'
        self.datelabel.config(text=txt)
        self.datelabel.update()

        # pause after endtime
        if self.displaytime > self.endtime:
            self.pause = True

        return

    def change_color(self,color):
        bg = '#'+bytes([color,color,color]).hex()
        self.canvas.itemconfig(self.clkface, fill=bg)
        return

    @staticmethod
    def interpolate(x1, y1, x2, y2, seek):
        X = x1 + ((x2-x1)*seek)
        Y = y2 + (y2-y1)*(X - x2)/(x2 - x1)
        return(X,Y)

class tmy():
    """
    Gets Typical meterological year from PVGIS and stores the dat for the days of interest.

    The constructor takes the lat and long and the range of dates as a list of datetime objects: [startdate, enddate].  The first thing the constructor will do is fetch the
    TMY data from the PVGIS online database.  Next it will coerce the time series to the year 2000.
    The data is all in UTC time and is timezone aware, the daterange may or may not be timezone aware so if not, the lat
    and lng will be used to determine the timezone
    """
    def __init__(self, lat=39.13, lng=-77.21, tz = timezone(timezones(39.13, -77.21).tz), daterange=[datetime.now().replace(year=2000), datetime.now().replace(year=2000) + timedelta(days=1)]):

        # get the TMY data for the lat and long
        tmydata = iotools.get_pvgis_tmy(lat, lng, map_variables=True)
        tmydata = self.coerce_tmy_year(tmydata)

        # coerce the daterange into the desired timezone
        self.tz = tz
        #self.daterange = self.coerce_daterange_year(daterange)
        if daterange[0].tzinfo is None or daterange[0].utcoffset() is None:
            daterange[0] = self.tz.localize(daterange[0])
            daterange[1] = self.tz.localize(daterange[1])

        # we need to convert the localized daterange to UTC time to get the correct tmy slice
        daterange_utc = self.local_to_utc(daterange)

        # get the slice of TMY data for the date range
        self.tmy_slice = tmydata[0][daterange_utc[0] - timedelta(hours=3):daterange_utc[1] + timedelta(hours=3)]

        # these times are in UTC so we need to localize them
        self.tmy_slice.index = self.tmy_slice.index.tz_convert(self.tz)
        self.tmy_slice.index = self.round_to_nearest_hour(self.tmy_slice.index)

    @staticmethod
    def coerce_tmy_year(tmydata):
        """ The TMY timeseries takes months of data from different years, this wil coerce them all to 2000 so we can
            later pick a range of dates
        """
        data_ymd = tmydata[0].index
        data_ymd = data_ymd.map(lambda datetime: datetime.replace(year=2000))
        tmydata[0].index = data_ymd
        return tmydata


    @staticmethod
    def coerce_daterange_year(dt):
        for i in range(len(dt)):
            dt[i] = dt[i].replace(year=2000)
        return dt

    @staticmethod
    def local_to_utc(dt):
        daterange_utc = []
        for i in range(len(dt)):
            daterange_utc.append(dt[i].astimezone(utc))
        return daterange_utc

    @staticmethod
    def round_to_nearest_hour(ymdh):
        dt_half_hour = ymdh[0].replace(minute=30, second=0, microsecond=0)
        if ymdh[0] >= dt_half_hour:
            ymdh = ymdh.map(lambda datetime: datetime.replace(minute=0, second=0, microsecond=0)  + timedelta(hours=1))
        else:
            ymdh = ymdh.map(lambda datetime: datetime.replace(minute=0, second=0, microsecond=0))
        return ymdh



if __name__=='__main__':
     root= tmy_clock(speed=4098)

     while True:
         root.update()
         root.update_idletasks()
         root.update_class()

    # debugging tmy stand-alone
    # root = tmy()
    # print(root.tmy_slice)
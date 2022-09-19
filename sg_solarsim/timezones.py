""" timezones.py
    Constructor finds the timezone from latitude and longitude.
    a method replace_dt_tz() iterates through a list of datettime objects and replaces the timezone
"""

from datetime import datetime, timedelta
from pytz import timezone, utc
from pytz.exceptions import UnknownTimeZoneError

from timezonefinder import TimezoneFinderL

class timezones:
    """
   Constructor finds the timezone from latitude and longitude.
    a method replace_dt_tz() iterates through a list of datettime objects and replaces the timezone
    """


    def __init__(self, lat, lng):
        tf = TimezoneFinderL()
        self.tz = tf.timezone_at(lng=lng, lat=lat)
        del tf

    def get_tz(self):
        return self.tz

    def get_timeinfo(self):
        return timezone

    def localize(self,dt):
        """
        replaces the tzinfo with the tz from the creation of this object
        :param dt: list of datetime objects
        :return:  list of localized datetime objects
        """
        try:
            local = timezone(self.tz)
            for i in range(len(dt)):
                dt[i] = dt[i].replace(tzinfo=local)

        except UnknownTimeZoneError:
            raise

        return dt


if __name__ == '__main__':
    tz = timezones(39.13, -77.21,)
    dt = [datetime.now(), datetime.now() + timedelta(days=1)]
    print(dt)
    dt = tz.localize(dt)
    print(dt)
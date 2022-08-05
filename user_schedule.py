import datetime
from datetime import date

class UserSchedule:

    def __init__(self, userDays):
        self.userDays = userDays
    

    def caluclateDay():
        import calendar

        return (calendar.day_name[datetime.date.today().weekday()]), (datetime.datetime.now().weekday())


    def strip_time(self, day):

        time_to_strip = self.userDays[day] 











import datetime
from datetime import date

def calculateDay():

    import calendar

    return calendar.day_name[date.today().weekday()], datetime.datetime.now().weekday()


def userSchedule():

    userDays = {'Monday':'10:00 AM','Tuesday': '12:00 PM', 'Wednesday':'12:45 PM','Thursday':'11:00 PM', 'Friday':'9:00 AM', 'Saturday':'11:30 PM', 
                'Sunday':'8:30 AM'}

    day_name, day_integer = calculateDay()

    try:

        if (day_name in userDays.keys()):

                preffered_time = userDays[day_name]


                in_time = datetime.datetime.strptime(preffered_time, "%I:%M %p")

                out_time = datetime.datetime.strftime(in_time, "%H:%M")

                out_time_split = out_time.split(":")



                newdaytime = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,datetime.datetime.now().day,int(out_time_split[0]), 
                                            int(out_time_split[1])).replace(microsecond=0)

                return newdaytime.isoformat()

        raise Exception

    except:
        print("Sorry I can't execute today. Add me in the schedule if you want me to work ;)")
        exit(0)



    
userSchedule()







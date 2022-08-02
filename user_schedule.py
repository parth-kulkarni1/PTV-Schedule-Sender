import datetime
from datetime import date

def calculateDay():

    import calendar

    return calendar.day_name[date.today().weekday() + 1], datetime.datetime.now().weekday()


def userSchedule():


    day_name, day_integer = calculateDay()

    print(day_name)

    userDays = {'Monday': '11:00 AM', 'Wednesday':'12:00 PM', 'Friday':'11:00 AM', 'Sunday':'11:00 AM'}

    for i in userDays.keys():
        if str(i) == str(day_name):

            preffered_time = userDays[day_name]


            in_time = datetime.datetime.strptime(preffered_time, "%I:%M %p")

            out_time = datetime.datetime.strftime(in_time, "%H:%M")

            out_time_split = out_time.split(":")

            newdaytime = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,datetime.datetime.now().day + 1,int(out_time_split[0]), 
                                        int(out_time_split[1])).replace(microsecond=0)

            return newdaytime

    else:
        print("Sorry I can't execute today. Add me in the schedule if you want me to work ;)")
        exit(0)



    
userSchedule()







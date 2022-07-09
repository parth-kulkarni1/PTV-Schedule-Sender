import hmac
import hashlib
import json
import requests
import geocoder
import datetime

def checkAPIStatusCode(requestObj):

    try:
        if requestObj.status_code != 200:
            raise Exception
    
    except:
        print("Error has occured with query. The API error code is", requestObj.status_code)


def convertLocalTimeToUTC(user_local_time):

    conversion = (user_local_time[11:16])

    index = 11


    ptv_clock_utc_reset = "10:00 AM"
    
    if conversion == '10:00':
        val = '00'

    elif conversion > ptv_clock_utc_reset:
        val = str(int(conversion[0:2]) - 10)

        if int(val) < 10:
            val = val.zfill(2)
    
    else:
        val = str(abs(int(conversion[0:2]) - 10))

        val = str(24 - int(val))

    
    return user_local_time[:index] + val + user_local_time[index + 2:]
    
def convertUTCTimeToLocal(utctime_iso):

    import dateutil.parser
    import pytz
    
    utctime = dateutil.parser.parse(utctime_iso)

    localtime = utctime.astimezone(pytz.timezone("Australia/Melbourne"))

    return localtime




def getAPI(apiRequest, devIdPara = '?'):

    devid = 3002170
    devkey = b'130e7f10-eadb-4236-808a-05e18250e0ec'
    baseURL = 'http://timetableapi.ptv.vic.gov.au'

    updated_msg = '/v3/' + apiRequest + devIdPara + 'devid=' + str(devid)

    sig = hmac.new(devkey, updated_msg.encode('utf-8'),hashlib.sha1).hexdigest().upper()
    url = baseURL  + updated_msg + '&signature=' + sig

    apiContent = requests.get(url)

    checkAPIStatusCode(apiContent) # This will check whether a sucessful API call has been established.

    json_obj = apiContent.json()

    print(url)


    return json_obj

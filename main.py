import hmac
import hashlib
import json
import requests
import geocoder
import datetime

from my_info import my_adderess, my_bing_key, my_route_type, my_suburb     # Imports your adderess from the my_info.py file.
from user_schedule import userSchedule

def checkAPIStatusCode(requestObj):

    try:
        if requestObj.status_code != 200:
            raise Exception
    
    except:
        print("Error has occured with query. The API error code is", requestObj.status_code)


def convertLocalTimeToUTC(user_local_time):


    ptv_clock_reset = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,datetime.datetime.now().day + 1, 10,0,0,0)

    print(user_local_time,ptv_clock_reset)

    
    if user_local_time < ptv_clock_reset:
        g = ((user_local_time - ptv_clock_reset))
        time_utc = (str(g).split(",")[1].strip())
        time_utc = time_utc.split(":")
        new_time = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, int(time_utc[0]),int(time_utc[1]),int(time_utc[2]))
    
    elif user_local_time >= ptv_clock_reset:
        g = ((user_local_time - ptv_clock_reset))
        time_utc = str(g).strip().split(":")
        new_time = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day + 1, int(time_utc[0]), int(time_utc[1]), int(time_utc[2]))
    

    return new_time.isoformat()
    

    
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


def retriveStations_NearMe():

    g = geocoder.bing(my_adderess,key = my_bing_key) # You change adderess to suburub .Returns the latitude and longititude of provided adderess in a list

    lattitude,longititude = g.latlng

    default_max_radius = 15000 # This refers to the maximum radius from your location the API will look for retriving stop details. Change value as you please.

    max_query_returns = 3

    route_type_string= ''

    for i in my_route_type:
        route_type_string = route_type_string + 'route_types=' + str(i) + '&'


    json_obj = getAPI(apiRequest='stops/location/' + str(lattitude) + ',' + str(longititude) + '?' + route_type_string + 'max_results=' + str(max_query_returns) + '&' 
            + 'max_distance=' + str(default_max_radius), devIdPara='&')

    
    

    setting_my_preferred_station  = {'stop_id': str(json_obj['stops'][0]['stop_id']), 'stop_name': str(json_obj['stops'][0]['stop_name']), 
    'stop_suburb': str(json_obj['stops'][0]['stop_suburb']), 'route_type':str(json_obj['stops'][0]['route_type']), 'route_id': str(json_obj['stops'][0]['routes'][0]['route_id'])}

    #print(setting_my_preferred_station)

    return setting_my_preferred_station




def getDirectionID():

    station_info = retriveStations_NearMe()

    json_obj = getAPI(apiRequest='directions/route/' + str(station_info['route_id']))

    directionID = json_obj['directions'][1]['direction_id']

    return str(directionID)


def outputDepartures(): # Need multipule run_ref's to be returned from this query from each depeature.

    get_station_info = retriveStations_NearMe()
    user_time = userSchedule()

    json_obj = getAPI(apiRequest='departures/route_type/' + str(get_station_info['route_type']) + '/stop/'+ str(get_station_info['stop_id']) + 
                      '/route/' + str(get_station_info['route_id'] )+ '?direction_id=' + getDirectionID() + '&date_utc=' + convertLocalTimeToUTC(user_time) + '&max_results=3'+
                      '&include_geopath=false', devIdPara='&')
    
    run_refs = []

    for i in range(len(json_obj['departures'])):
        if json_obj['departures'][i]['scheduled_departure_utc'] >= convertLocalTimeToUTC(user_time):
            run_refs.append(json_obj['departures'][i]['run_ref'])
    
    print(run_refs)
    
    return run_refs



def getDepeatureSequence(json_obj,get_station_info):


    for i in range(len(json_obj['departures'])):
        if str(json_obj['departures'][i]['stop_id']) == get_station_info['stop_id']:
            return json_obj['departures'][i]['departure_sequence'] 
    



def outputStops():

        get_station_info = retriveStations_NearMe()
        user_time = userSchedule()

        message_string = ''

        route_counter = 1

        print(get_station_info['stop_name'])

        for i in range(len(outputDepartures())):
            json_obj = getAPI(apiRequest='pattern/run/' + outputDepartures()[i] + '/route_type/' + get_station_info['route_type'] + '?expand=All' 
                            + '&date_utc=' + convertLocalTimeToUTC(user_time), devIdPara='&')    
            
            departure_sequence = getDepeatureSequence(json_obj,get_station_info)    

            for j in range(departure_sequence - 1, len(json_obj['departures'])):
                stop_id = (json_obj['departures'][j]['stop_id']) 

                if str(json_obj['stops'][str(stop_id)]['stop_id']) == get_station_info['stop_id']:
                    message_string = message_string + '\n' + 'Route ' + str(route_counter) + ' :'
                    message_string = message_string + '\n' + '-----------'
                    route_counter +=1

                message_string = message_string + '\n' + (json_obj['stops'][str(stop_id)]['stop_name'] + ': ')
                g = convertUTCTimeToLocal(json_obj['departures'][j]['scheduled_departure_utc'])
                message_string = message_string + (str(g) + '\n')
                

        return message_string

outputStops()
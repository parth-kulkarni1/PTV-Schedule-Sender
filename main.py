import hmac
import hashlib
import json
from matplotlib.font_manager import json_dump
import requests
import geocoder
from my_info import my_adderess, my_bing_key, my_route_type, my_suburb     # Imports your adderess from the my_info.py file.
import datetime


def checkAPIStatusCode(requestObj):

    try:
        if requestObj.status_code != 200:
            raise Exception
    
    except:
        print("Error has occured with query. The API error code is", requestObj.status_code)


def convertLocalTimeToUTC():

    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()


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

    print()

    return json_obj


def retriveStations_NearMe():

    g = geocoder.bing(my_adderess,key = my_bing_key) # You change adderess to suburub .Returns the latitude and longititude of provided adderess in a list

    lattitude,longititude = g.latlng

    print(lattitude,longititude)

    default_max_radius = 15000 # This refers to the maximum radius from your location the API will look for retriving stop details. Change value as you please.

    max_query_returns = 3

    route_type_string= ''

    for i in my_route_type:
        route_type_string = route_type_string + 'route_types=' + str(i) + '&'


    json_obj = getAPI(apiRequest='stops/location/' + str(lattitude) + ',' + str(longititude) + '?' + route_type_string + 'max_results=' + str(max_query_returns) + '&' 
            + 'max_distance=' + str(default_max_radius), devIdPara='&')

    print(json_obj)
    

    setting_my_preferred_station  = {'stop_id': str(json_obj['stops'][0]['stop_id']), 'stop_name': str(json_obj['stops'][0]['stop_name']), 
    'stop_suburb': str(json_obj['stops'][0]['stop_suburb']), 'route_type':str(json_obj['stops'][0]['route_type']), 'route_id': str(json_obj['stops'][0]['routes'][0]['route_id'])}

    return setting_my_preferred_station




def getDirectionID():

    station_info = retriveStations_NearMe()

    json_obj = getAPI(apiRequest='directions/route/' + str(station_info['route_id']))

    directionID = json_obj['directions'][1]['direction_id']

    return str(directionID)


def outputDepartures(): # Need multipule run_ref's to be returned from this query from each depeature.

    get_station_info = retriveStations_NearMe()

    json_obj = getAPI(apiRequest='departures/route_type/' + str(get_station_info['route_type']) + '/stop/'+ str(get_station_info['stop_id']) + 
                      '/route/' + str(get_station_info['route_id'] )+ '?direction_id=' + getDirectionID() + '&date_utc=' + convertLocalTimeToUTC() +
                      '&include_geopath=false', devIdPara='&')
    
    run_refs = []
 
    for i in range(len(json_obj['departures'])):
        if json_obj['departures'][i]['scheduled_departure_utc'] >= convertLocalTimeToUTC():
            run_refs.append(json_obj['departures'][i]['run_ref'])     
    

    return run_refs


def getStation_Sequence_In_Route():

    get_station_info = retriveStations_NearMe()
    get_direction_id = getDirectionID()

    json_obj = getAPI(apiRequest='stops/route/' + get_station_info['route_id'] + '/route_type/' + get_station_info['route_type'] + '?direction_id=' 
                       +getDirectionID(), devIdPara='&')
    

    for i in range(len(json_obj['stops'])):
        if json_obj['stops'][i]['stop_suburb'] == get_station_info['stop_suburb']:
            return json_obj['stops'][i]['stop_sequence']



def outputStops():

    with open('journey.txt','w') as f:

        get_station_info = retriveStations_NearMe()

        start_stop_sequence = getStation_Sequence_In_Route()

        json_obj = getAPI(apiRequest='pattern/run/' + outputDepartures()[0] + '/route_type/' + get_station_info['route_type'] + '?expand=All' 
                        + '&date_utc=' + convertLocalTimeToUTC(), devIdPara='&')



        
        for i in range(start_stop_sequence - 1,len(json_obj['departures'])): # Have to -1 as counting in Python beings from 0
            stop_id = json_obj['departures'][i]['stop_id']
            f.write(json_obj['stops'][str(stop_id)]['stop_name'])
            f.write(json_obj['departures'][i]['scheduled_departure_utc'])
        






outputStops()
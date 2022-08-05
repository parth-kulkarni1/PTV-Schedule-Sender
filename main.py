import hmac, hashlib
import json
import requests
import geocoder
import datetime, dateutil.parser
import pytz
import os
from sqlitedict import SqliteDict
        

BASE_URL = 'http://timetableapi.ptv.vic.gov.au'
PTV_CLOCK_RESET = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,datetime.datetime.now().day + 1, 10,0,0,0)
devid = os.environ['DEV_ID_PTV']
devkey = bytes(os.environ['DEV_KEY_PTV'], encoding='utf- 8')
db = SqliteDict("user_station_preferences.sqlite", autocommit=True)

my_adderess = "7 ...., Hoppers Crossing, 3029, Victoria, Australia" # Enter your aderess in this variable
my_bing_key = "AlfA8xF6WBgesbzwkw1nbf28l0joj2mbba-DagPz_bL1b5vArsuWMP7o6srflx_J" # Enter your basic bing maps key in this variable
my_route_type = [0,3] # 0 - Metro Trains, 1 - Tram, 2 - Bus, 3 - V/Line and Coach, 4 - NightRider
my_suburb = 'Hoppers Crossing'



def checkAPIStatusCode(requestObj):
    try:
        if requestObj.status_code != 200:
            raise Exception
    
    except:
        print("Error has occured with query. The API error code is", requestObj.status_code)


def getAPI(apiRequest, devIdPara = '?'):

    updated_msg = '/v3/' + apiRequest + devIdPara + 'devid=' + str(devid)

    sig = hmac.new(devkey, updated_msg.encode('utf-8'),hashlib.sha1).hexdigest().upper()
    url = BASE_URL  + updated_msg + '&signature=' + sig

    apiContent = requests.get(url)

    checkAPIStatusCode(apiContent) # This will check whether a sucessful API call has been established.

    json_obj = apiContent.json()

    return json_obj



class ApiFunctions:

    def __init__(self, user_local_time, utc_time_iso):
        self.user_local_time = user_local_time
        self.utc_time_iso = utc_time_iso


    def getCurrentDateString(self, reset = False, hour = 0, minutes = 0, seconds = 0):

        if reset == False:
            datetime_obj = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day + 0, hour, minutes, seconds)

        else:
            datetime_obj = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day + 1, hour, minutes, seconds)

        return datetime_obj.isoformat()

    def convertLocalTimeToUTC(self):

        caluclated_string = self.user_local_time - PTV_CLOCK_RESET

        
        if self.user_local_time < PTV_CLOCK_RESET:
            time_utc = (str(caluclated_string).split(",")[1].strip())
            time_utc = time_utc.split(":")
            api_utc_time = self.getCurrentDateString(reset=False, hour = int(time_utc[0]), minutes = int(time_utc[1]), seconds = int(time_utc[2]))
        
        else:
            time_utc = str(caluclated_string).strip().split(":")
            api_utc_time = self.getCurrentDateString(reset=True, hour = int(time_utc[0]), minutes = int(time_utc[1]), seconds = int(time_utc[2]))
        

        return api_utc_time
        

        
    def convertUTCTimeToLocal(self):

        utctime = dateutil.parser.parse(self.utc_time_iso)

        localtime = utctime.astimezone(pytz.timezone("Australia/Melbourne"))

        return localtime
    

    def route_string_builder(self):

        route_type_string = ''

        for i in my_route_type:
            route_type_string = route_type_string + 'route_types=' + str(i) + '&a'
        

        return route_type_string


class UserStationInfo(ApiFunctions):

    def __init__(self, my_adderess, my_bing_key):

        self.my_adderess = my_adderess
        self.my_bing_key = my_bing_key

    
    def get_coordinates(self):

        g = geocoder.bing(self.my_adderess,key =self.my_bing_key) # You change adderess to suburub .Returns the latitude and longititude of provided adderess in a list

        lattitude,longititude = g.latlng

        return lattitude, longititude
    

        
    def setPrefferedStation(self, json_obj):

        '''Made a litle user input box, that will take the user's input and extract the information of their preffered station'''

        station_info = None


        if len(db) == 0:

            user_stations_nearby = []

            print("Pick a preffered Station please. Enter Y to proceed or N to quit. If you press N the closet Station will be chosen.\n")

            for i in range(len(json_obj['stops'])):
                user_stations_nearby.append(str(json_obj['stops'][i]['stop_name']).strip())

            user_start_input = input()

            if user_start_input.lower() == 'y':
                print("Stations near you are:")
                print(user_stations_nearby)

                station_selected = input("Pick one of the following stations, by typing it's name with spaces and corrrect cases : ").strip()
            
                for i in range(len(json_obj['stops'])):
                    if str(json_obj['stops'][i]['stop_name']).strip() == station_selected:
                        print("Station Found")
                        station_info = json_obj['stops'][i]
                
                print("Saving station information...")
                
                db["station"] = station_info

            else:

                nearest_station = json_obj['stops'][0]['stop_distance'] # Intalise the variable as the first element in list of Nearby Stations.


                for i in range(len(json_obj['stops'])):
                    if json_obj['stops'][i]['stop_distance'] <= nearest_station:
                        station_info = json_obj['stops'][i]
                
                print("Saving station information...")

                db["station"] = station_info

        
        else:
            print("Station is already saved. You saved the following station:")
            print()

            for key, item in db.items():
                    print("%s=%s" % (key, item))
        

        
    def retriveStations_NearMe(self):

        lattitude, longititude = self.get_coordinates()

        DEFAULT_MAX_RADIUS = 15000 # This refers to the maximum radius from your location the API will look for retriving stop details. Change value as you please.
        MAX_QUERY_RETURNS = 3 

        json_obj = getAPI(apiRequest='stops/location/' + str(lattitude) + ',' + str(longititude) + '?' + super().route_string_builder() 
                   + 'max_results=' + str(MAX_QUERY_RETURNS) + '&' + 'max_distance=' + str(DEFAULT_MAX_RADIUS), devIdPara='&')
        
        self.setPrefferedStation(json_obj)
    

    def getDirectionID(self): # We gonna have to print out all possible routes then, force user to pick a route, and store that within the db. Then we extract directonID

        json_obj = getAPI(apiRequest='directions/route/' + str(db['station']['routes']['route_id']))

        print(json_obj)

'''

class JourneyInfo(UserStationInfo, ApiFunctions):


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
            
        return run_refs



    def getDepeatureSequence(json_obj,get_station_info):


        for i in range(len(json_obj['departures'])):
            if str(json_obj['departures'][i]['stop_id']) == get_station_info['stop_id']:
                return json_obj['departures'][i]['departure_sequence'] 


    def outputStops():

        with open("journey.txt",'w') as f:

            get_station_info = retriveStations_NearMe()
            user_time = userSchedule()

            message_string = ''

            route_counter = 1

            print(get_station_info['stop_name'])



            for i in range(len(outputDepartures())):
                json_obj = getAPI(apiRequest='pattern/run/' + outputDepartures()[i] + '/route_type/' + get_station_info['route_type'] + '?expand=All' 
                                    + '&date_utc=' + convertLocalTimeToUTC(user_time), devIdPara='&')    
                
                #print(json.dumps(json_obj, indent = 4))
                    
                departure_sequence = getDepeatureSequence(json_obj,get_station_info)  

                finish_sequence = finishSequence(json_obj)  

                print("Finish sequence is", finish_sequence)

                for j in range(departure_sequence - 1, int(finish_sequence)):
                    stop_id = (json_obj['departures'][j]['stop_id']) 

                    if str(json_obj['stops'][str(stop_id)]['stop_id']) == get_station_info['stop_id']:
                        message_string = message_string + '\n' + 'Route ' + str(route_counter) + ' :'
                        message_string = message_string + '\n' + '-----------'
                        route_counter +=1

                    message_string = message_string + '\n' + (json_obj['stops'][str(stop_id)]['stop_name'] + ': ')
                    g = convertUTCTimeToLocal(json_obj['departures'][j]['scheduled_departure_utc'])
                    message_string = message_string + (str(g) + '\n')
                
                
            
            f.write(message_string)

            return message_string

outputStops()

'''

def main():
    UserStationInfo_info = UserStationInfo(my_adderess, my_bing_key)
    json = UserStationInfo_info.retriveStations_NearMe()
    print(json)

    UserStationInfo_info.getDirectionID()



if __name__ == "__main__":
    main()

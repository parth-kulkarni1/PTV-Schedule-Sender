import datetime
import time

my_adderess = "7 Scherbourg Place, Hoppers Crossing, 3029, Victoria, Australia" # Enter your aderess in this variable
my_bing_key = "AlfA8xF6WBgesbzwkw1nbf28l0joj2mbba-DagPz_bL1b5vArsuWMP7o6srflx_J" # Enter your basic bing maps key in this variable
my_route_type = [3] # 0 - Metro Trains, 1 - Tram, 2 - Bus, 3 - V/Line and Coach, 4 - NightRider
my_suburb = ''
my_day = 'Monday' # Make daytime objecs, so you can easily convert it into UTC Times. 

my_day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']


def nownomicro():
  ''' Returns current time, without microseconds, as required by PTV API.'''
  return datetime.datetime.utcnow().replace(microsecond=0)

def now8601():
  ''' Returns current time, without microseconds, as required by PTV API, in 8601 format.'''
  return nownomicro().isoformat()


print(now8601())

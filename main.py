import hmac
import hashlib
import json

devid = 3002170
devkey = b'130e7f10-eadb-4236-808a-05e18250e0ec'

updated_msg = '/v3/disruptions?devid=' + str(devid)

sig = hmac.new(devkey, updated_msg.encode('utf-8'),hashlib.sha1).hexdigest().upper()
url = 'http://timetableapi.ptv.vic.gov.au' + updated_msg + '&signature=' + sig

print(url)
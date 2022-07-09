from twilio.rest import Client
import keys
from main import outputStops
from datetime import datetime

client = Client(keys.account_sid, keys.auth_token)

message = client.messages.create(
    body = '\n' +  'Schedule for Today' + str(datetime.date) + '\n' + outputStops(),
    from_ = keys.my_phone_number,
    to = keys.target_phone_number
)

print(message.body)

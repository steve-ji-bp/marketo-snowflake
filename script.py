from marketorestpython.client import MarketoClient
import configparser

config = configparser.ConfigParser()
config.read('cred.config')
munchkin_id = config.get('Marketo Credentials', 'munchkin_id')
client_id = config.get('Marketo Credentials', 'client_id')
client_secret = config.get('Marketo Credentials', 'client_secret')
api_limit = None
max_retry_time = None
mc = MarketoClient(munchkin_id, client_id, client_secret, api_limit, max_retry_time)

for i in range(5):
  lead = mc.execute(method = 'get_lead_by_id', id = i+1)
  print(lead)

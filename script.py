from marketorestpython.client import MarketoClient
import configparser

config = configparser.ConfigParser()
config.read('cred.config')
munchkin_id = config.get('Marketo Credentials', 'munchkin_id')
client_id = config.get('Marketo Credentials', 'client_id')
client_secret = config.get('Marketo Credentials', 'client_secret')
mc = MarketoClient(munchkin_id, client_id, client_secret)
lead = mc.execute(method = 'get_lead_by_id', id = 1001)
print(lead)

import snowflake.connector
import os
import configparser
import pandas as pd
import numpy as np
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization
from marketorestpython.client import MarketoClient
import json

# Get passkey from config file
config = configparser.ConfigParser()
config.read('cred.config')
passkey = config.get('Snowflake Credentials', 'passkey')

os.environ['SNOWFLAKE_PRIVATE_KEY_PASSPHRASE'] = passkey

with open("/Users/stevej/snowflake-key/rsa_key.p8", "rb") as key:
    p_key= serialization.load_pem_private_key(
        key.read(),
        password=os.environ['SNOWFLAKE_PRIVATE_KEY_PASSPHRASE'].encode(),
        backend=default_backend()
    )

pkb = p_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption())

ctx = snowflake.connector.connect(
    user='stevej',
    account='wz88589.us-east-1',
    private_key=pkb)

cs = ctx.cursor()

# Use correct role, warhouse, schema
cs.execute("use role airflow_role")
cs.execute("use warehouse demo_wh")
cs.execute("use schema moby_central.learning_sql")
cs.execute("select id, first_name, last_name from customers")
for (id, first_name, last_name) in cs:
    print('{0}, {1}, {2}'.format(id, first_name, last_name))


cs.execute("select * from customers")
print(','.join([col[0] for col in cs.description]))
print(cs.sfqid)


# Marketo Connection
munchkin_id = config.get('Marketo Credentials', 'munchkin_id')
client_id = config.get('Marketo Credentials', 'client_id')
client_secret = config.get('Marketo Credentials', 'client_secret')
api_limit = None
max_retry_time = None
mc = MarketoClient(munchkin_id, client_id, client_secret, api_limit, max_retry_time)

import requests

resp = requests.get('https://' + munchkin_id + '.mktorest.com/identity/oauth/token?grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret)
print(json.loads(resp.text))

j0 = json.loads(resp.text)
j0
token_type = j0['token_type'].capitalize()
acc_token = j0['access_token']
print(acc_token)
headers = {'Authorization': token_type + ' ' + acc_token}
print(headers)

url = 'https://' + munchkin_id + '.mktorest.com/rest/v1/campaigns.json'
r = requests.get(url, headers=headers)
data = json.loads(r.text)
print(data['nextPageToken'])
counter = 1
print("page = " + str(counter))
while 'nextPageToken' in data:
    url = url + '?nextPageToken=' + data['nextPageToken']
    r = requests.get(url, headers = headers)
    data = json.loads(r.text)
    counter = counter + 1
    print("page = " + str(counter))

print("reached End of File")

results = data['result']
type(results[0])

df = pd.DataFrame(results)
df.head()
df.dtypes
df['updatedAt'] = pd.to_datetime(df['updatedAt'])
df['updatedAt']
# lead = list()
# for i in range(5):
#   lead.append(mc.execute(method = 'get_lead_by_id', id = i+1))
#   print(lead)
#
# print(json.dumps([{'lead':x} for x in lead],indent = 2))
# lead[0]
#
# lead = mc.execute(method = 'describe')
# print(lead)
#
# lead
ctx.close()

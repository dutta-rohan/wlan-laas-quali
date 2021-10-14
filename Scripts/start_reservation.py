import requests
import json



# Login to Sandbox API and get back Authorization token to use for later calls, auth token should timeout within 10 minutes by default
url = 'http://localhost:82/api/login'
headers = {'content-type': 'application/json'}
data = {
       "username":"admin",
       "password":"admin",
       "domain":"Global"
       }
response = requests.put(url, data=json.dumps(data), headers=headers)
auth_token = response.text.replace('"', '')
print('Basic {}'.format(auth_token))




# Start Sandbox from Blueprint Basic Lab
basic_lab_id = "5e843b4f-2bfd-4a39-b754-91cb0bca0100"
url = 'http://localhost:82/api/v2/blueprints/{}/start'.format(basic_lab_id)
headers = {'content-type': 'application/json', 'Authorization': 'Basic {}'.format(auth_token)}
data = {
       "name":"QualiTesting",
       "duration":"PT6H5M",
       "params":[
          {
             "name":"Chart Version",
             "value":"main"
          },
          {
             "name":"owgw Version",
             "value":"master"
          },
          {
             "name":"owsec Version",
             "value":"main"
          },
          {
             "name":"owfms Version",
             "value":"main"
          },
          {
             "name":"owgwui Version",
             "value":"main"
          },
          {
             "name":"Wifi type",
             "value":"[Any]"
          },
          {
             "name":"AP Model",
             "value":"EAP101"
          }
       ],
       "permitted_users":[
          "admin"
       ]
       }

response = requests.post(url, data=json.dumps(data), headers=headers)
print(response)
print(response.text)

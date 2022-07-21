#import dependencies
import datetime
import json
import datetime
import sys
try:
    import requests
except:
    print("FatalError:requests library could not import")
    sys.exit(1)

#define constants
TENANT_ID = 'b3d72242-8320-4894-beec-0323223fd044'
CLIENT_SECRET = 'redacted'
APPLICATION_ID = '1341bbcf-2f2e-43cb-a3ee-04994454d2eb'
RESOURCE_ID = '05a65629-4c1b-48c1-a78b-804c4abdd4af'
ACTIVITIES_URL = 'https://seccomlab.us.portal.cloudappsecurity.com/api/v1/activities/'
OUTPUT_PATH = 'C:/TheMainframe/abaker@seccomlab.json'
START_DATE = '07/14/2022T0:00:00'
END_DATE = '07/21/2022T0:00:00'
#define token getter
def Get_AppToken(tenantID, clientSecret, clientID, resourceAppID):
    oAuthUri = "https://login.microsoftonline.com/%s/oauth2/token"%(tenantID)
    # defining a params dict for the parameters to be sent to the API
    grantType = 'client_credentials'
    postParams = {'resource':resourceAppID,
                  'client_id':clientID,
                  'client_secret':clientSecret,
                  'grant_type':grantType}
    # sending get request and saving the response as response object
    r = json.loads(requests.post(url = oAuthUri, data = postParams).content)
    return r['access_token']

token = Get_AppToken(TENANT_ID,CLIENT_SECRET,APPLICATION_ID,RESOURCE_ID)

if not token:
    print("FatalError:failed to get auth token")
    sys.exit(1)
        
headers = {
    'Authorization':'Bearer {}'.format(token),
}

#generate start and end timestamps, multiply by 1000 to convert from seconds to ms
startDateElement = datetime.datetime.strptime(START_DATE,"%m/%d/%YT%H:%M:%S")
startTime = datetime.datetime.timestamp(startDateElement) * 1000

endDateElement = datetime.datetime.strptime(END_DATE,"%m/%d/%YT%H:%M:%S")
endTime = datetime.datetime.timestamp(endDateElement) * 1000

filters = {
    'date': {'range': {'start': startTime, 'end':endTime}},
}

request_data = {
    'filters': filters,
    'isScan': True,
    'limit': 5000
}

records = []
has_next = True
while has_next:
    r = requests.post(ACTIVITIES_URL, json=request_data, headers=headers)
    #r = requests.Request("POST",ACTIVITIES_URL, json=request_data, headers=headers)
    #prepared = r.prepare()
    content = json.loads(requests.post(ACTIVITIES_URL, json=request_data, headers=headers).content)
    response_data = content.get('data', [])
    records += response_data
    #print('Got {} more records'.format(len(response_data)))
    has_next = content.get('hasNext', False)
    request_data['filters'] = content.get('nextQueryFilters')
    with open(OUTPUT_PATH, "a", encoding="utf-8") as outfile:
     json.dump(response_data, outfile, indent=4)

print('Got {} records in total'.format(len(records)))
print('Output results to %s'%OUTPUT_PATH)
import requests
import json

header = {"Content-Type": "application/json; charset=utf-8",
          "Authorization": "Basic YTkxZTI2YTUtMWEwMC00NWIxLTljMDctYTQ4OWE1MDgwYTNm"}

payload = {"app_id": "dfd59359-2563-45da-bec1-651473edf1fd",
           "included_segments": ["All"],
           "contents": {"en": "English Message"},
           "big_picture":"http://www.indianrail.gov.in/enquiry/images/slide.jpg"}
 
req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
 
print(req.status_code, req.reason)

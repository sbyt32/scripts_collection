# Scyfall Scraper
# Pulls the bulk data from Scryfall and stores it locally in a folder.
# File Name is based on the last updated date from Scryfall.
# ! There is no plan if the URL fails to fetch!
# Test Data Below
# bulk_data_link = {
#     "data": 
#         [
#             {
#                 "updated_at": "2023-01-09T10:05:00.512+00:00",
#                 "type": "default_cards"
#             }
#         ]
# }

import requests
import re
import json
import os

def send_request(url:str):
  resp = requests.get(url)
  
  if not resp.ok:
    pass
  else:
    return resp.json()
  
bulk_data_link = send_request('https://api.scryfall.com/bulk-data')

for bulk_data_info in bulk_data_link['data']:
  if bulk_data_info['type'] == 'default_cards':
    regex_pattern = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}.*[0-9]{2}:[0-9]{2}:[0-9]{2}', re.IGNORECASE)
    fetch_time = re.search(regex_pattern, bulk_data_info['updated_at'])

    if fetch_time:
        
        file_name = fetch_time.group()
      
        file_name = file_name.replace("T", "_")
        file_name = file_name.replace(":","")
        all_data = send_request(bulk_data_info['download_uri'])
        
        if not os.path.exists('data'):
            os.mkdir('data')
        
        with open(f'data/{file_name}.json', 'w') as bulk_data_fp:
            json.dump(all_data, bulk_data_fp)

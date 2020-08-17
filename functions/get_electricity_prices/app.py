import requests

def lambda_handler(event, context):
    
    payload = {'chart_keys': 'prices_last_five_mins_map'}
    r = requests.get('https://www.electricityinfo.co.nz/dashboard/updates', params=payload)

    print (r.text)

    return {}
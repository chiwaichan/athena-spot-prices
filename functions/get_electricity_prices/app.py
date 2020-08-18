import requests
import os
import pickle
import boto3
import time
import json

def lambda_handler(event, context):
    
    bucketName = os.environ['PricesElectrictyInfoS3Bucket']

    payload = {'chart_keys': 'prices_last_five_mins_map'}
    r = requests.get('https://www.electricityinfo.co.nz/dashboard/updates', params=payload)

    parsed_json = (json.loads(r.text))

    jsonFileData = {}
    
    for n in parsed_json['charts']['prices_last_five_mins_map']['data']['nodes']:
        jsonFileData[n['gip_gxp_full']] = n['price']
        jsonFileData['date_time'] = n['trading_date'] + " " + str(n['market_time'])

    s3 = boto3.resource('s3')
    obj = s3.Object(bucketName, 'electricity-info-' + time.strftime("%Y%m%d%H%M") + '.json')
    obj.put(Body=json.dumps(jsonFileData))

    return {}
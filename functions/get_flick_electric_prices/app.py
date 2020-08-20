import requests
import os
import pickle
import boto3
import time
import json
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    secret_name = "flick-electric-credentials"
    region_name = os.environ['AWS_REGION']

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        else:
            print(e)
    else:
        if 'SecretString' in get_secret_value_response:
            text_secret_data = get_secret_value_response['SecretString']
            credentials = json.loads(text_secret_data)

            r = requests.post('https://api.flick.energy/identity/oauth/token', data = {'grant_type':'password',
                                                                                        'client_id':'le37iwi3qctbduh39fvnpevt1m2uuvz',
                                                                                        'client_secret':'ignwy9ztnst3azswww66y9vd9zt6qnt',
                                                                                        'username': credentials["username"],
                                                                                        'password': credentials["password"]})

            token_json = (json.loads(r.text))

            r = requests.get('https://api.flick.energy/customer/mobile_provider/price', headers = {'Authorization':'Bearer ' + token_json['id_token']})

            price_json = (json.loads(r.text))

            bucketName = os.environ['PricesFlickElectricS3Bucket']

            jsonFileData = {}

            jsonFileData['date_time'] = price_json['needle']['now']
            jsonFileData['price'] = price_json['needle']['price']
            
            for comp in price_json['needle']['components']:
                jsonFileData[comp['charge_setter']] = comp['value']

            s3 = boto3.resource('s3')
            obj = s3.Object(bucketName, 'flick-electric-' + time.strftime("%Y%m%d%H%M") + '.json')
            obj.put(Body=json.dumps(jsonFileData))

    return {}
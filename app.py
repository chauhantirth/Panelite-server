from flask import Flask, jsonify, request
import toml
import os
from pathlib import Path
import db
import base64
import random

BASE_DIR = Path(os.getcwd())

with open(BASE_DIR / 'config.toml', 'r') as config_file:
    config = toml.load(config_file)
    API_PORT = config.get('API_PORT')
    API_HOST = config.get('API_HOST')
    IS_DEV = config.get('IS_DEVELOPMENT')

def getUserData(user):
    userData = user.copy()
    userData.pop('userAuthDetails', None)

    for org in db.org_details['orgs']:
        if org['orgId'] == user['associatedOrgId']:
            userData['orgName'] = org['orgName']
            userData['orgNameShort'] = org['orgNameShort']
            userData['orgLocation'] = org['orgLocation']
            userData['orgCity'] = org['orgCity']
            userData['plantCapacity'] = org['orgPlantDetails']['plantCapacity']
            userData['plantNumberOfPanels'] = org['orgPlantDetails']['plantNumberOfPanels']

    return base64.b64encode(str(userData).encode()).decode()

def predictGeneration(dateInfo):
    date = int(dateInfo['timestamp'])
    return random.randint(490, 580)

app = Flask(__name__)

@app.route('/api/refresh', methods=['POST'])
def refresh():
    try:
        json_data = request.get_json()
        sessionToken = json_data['data']['sessionToken']

        for user in db.user_details['users']:
            if sessionToken == user['userAuthDetails']['sessionToken']:
                return jsonify({'status': 'success', 'container': {
            'sessionToken': user['userAuthDetails']['sessionToken'],
            'userData': getUserData(user)
        }})

        return jsonify({'status': 'failure', 'errorMsg': 'Invalid Token, Please Login Again.'})

    except Exception as error:
        print(error)
        return jsonify({'status': 'failure', 'errorMsg': 'Invalid payload format'})
    

@app.route('/api/login', methods=['POST'])
def login():
    try:
        json_data = request.get_json()
        userEmail = json_data['data']['userEmail']
        userPassword = json_data['data']['userPassword']

        if userEmail == '' or userPassword == '':
            return jsonify({'status': 'failure', 'errorMsg': 'Invalid Email or Password. Please Try again.'})

        for user in db.user_details['users']:
            if userEmail == user['userEmail']:
                if userPassword == user['userPassword']:
                    return jsonify({'status': 'success', 'container': {
                        'sessionToken': user['userAuthDetails']['sessionToken'],
                        'userData': getUserData(user)
                    }})
                else:
                    return jsonify({'status': 'failure', 'errorMsg': 'Invalid Email or Password. Please Try again.'})

        return jsonify({'status': 'failure', 'errorMsg': 'Email not registered, Please Contact Admin.'})

    except Exception as error:
        print(error)
        return jsonify({'status': 'failure', 'errorMsg': 'Invalid payload format'})
    

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        json_data = request.get_json()
        sessionToken = json_data['data']['sessionToken']
        dateInfo = json_data['data']['dateInfo']

        for user in db.user_details['users']:
            if sessionToken == user['userAuthDetails']['sessionToken']:
                try:
                    if dateInfo['timestamp'] == '':
                        return jsonify({'status': 'failure', 'errorMsg': 'Invalid Date Recieved'})
                except Exception as e:
                    return jsonify({'status': 'failure', 'errorMsg': 'Date Information is missing'})
                
                return jsonify({'status': 'success', 'container': {
                    'predictedVal': str(predictGeneration(dateInfo)),
                    'unit': 'kWh'
                }})

        return jsonify({'status': 'failure', 'errorMsg': 'Unauthenticated Token, Please Login and Try Again.'})

    except Exception as error:
        print(error)
        return jsonify({'status': 'failure', 'errorMsg': 'Invalid payload format'})


# Run the app if this script is executed
if __name__ == '__main__':
    app.run(API_HOST, API_PORT, debug=config.get('IS_DEVELOPMENT'), use_reloader = True)
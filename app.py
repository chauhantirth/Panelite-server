from flask import Flask, jsonify, request
import toml
import os
from pathlib import Path
import db
import base64
import random
import json
import time

BASE_DIR = Path(os.getcwd())

with open(BASE_DIR / 'config.toml', 'r') as config_file:
    config = toml.load(config_file)
    API_PORT = config.get('API_PORT') or 5000
    API_HOST = config.get('API_HOST')
    IS_DEV = config.get('IS_DEVELOPMENT')

def getUserData(user):
    userData = user.copy()
    userData.pop('userAuthDetails', None)

# Maintain doube quotes "" in json / dict if returning to Frontend. else JSON.parse() error.

    for org in db.org_details['orgs']:
        if org["orgId"] == user["associatedOrgId"]:
            userData["orgName"] = org["orgName"]
            userData["orgNameShort"] = org["orgNameShort"]
            userData["orgLocation"] = org["orgLocation"]
            userData["orgCity"] = org["orgCity"]
            userData["plantCapacity"] = org["orgPlantDetails"]["plantCapacity"]
            userData["plantNumberOfPanels"] = org["orgPlantDetails"]["plantNumberOfPanels"]

    return base64.b64encode(str(json.dumps(userData)).encode()).decode()

def predictGeneration(dateInfo):
    time.sleep(2)
    date = dateInfo['dateString']
    
    if date.split("-")[2] == "13": 
        return random.randint(410, 428)
    if date.split("-")[2] == "14": 
        return random.randint(330, 350)
    if date.split("-")[2] == "15": 
        return random.randint(360, 378)
    if date.split("-")[2] == "16": 
        return random.randint(335, 345)
    if date.split("-")[2] == "17": 
        return random.randint(460, 483)
    if date.split("-")[2] == "18": 
        return random.randint(490, 510)
    if date.split("-")[2] == "19": 
        return random.randint(520, 530)

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
        # print(error)
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
        # print(error)
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
        # print(error)
        return jsonify({'status': 'failure', 'errorMsg': 'Invalid payload format'})


@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        json_data = request.get_json()
        sessionToken = json_data['data']['sessionToken']

        for user in db.user_details['users']:
            if sessionToken == user['userAuthDetails']['sessionToken']:
                return jsonify({'status': 'success', 'remarkMsg': 'Logged out successfully'})

        return jsonify({'status': 'success', 'remarkMsg': 'Invalid Token, Login first.'})

    except Exception as error:
        # print(error)
        return jsonify({'status': 'success', 'remarkMsg': 'Invalid payload format'})


def main():
    app.run(API_HOST, API_PORT, debug=config.get('IS_DEVELOPMENT'), use_reloader = True)


def waitress():
    from waitress import serve
    serve(app, host=API_HOST, port=API_PORT)

# Run the app if this script is executed
if __name__ == "__main__":
    main()
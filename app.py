from flask import Flask, jsonify, request
import toml
import os
from pathlib import Path

BASE_DIR = Path(os.getcwd())

with open(BASE_DIR / 'config.toml', 'r') as config_file:
    config = toml.load(config_file)
    API_PORT = config.get('API_PORT')
    API_HOST = config.get('API_HOST')

print(config)

app = Flask(__name__)

@app.route('/api/refresh', methods=['POST'])
def refresh():
    try:
        json_data = request.get_json()

        if json_data['data']['sessionToken'] not in ['token1', 'token2']: 
            return jsonify({'status': 'failure', 'errorMsg': 'Invalid Token, Please Login Again.'})
        
        else:
            return jsonify({'status': 'success', 'container': {
                'sessionToken': json_data['sessionToken'],
                'userData': 'eyJ1c2VySWQiOiIwNmQ2MDdlZC04NTRiLTRkZWYtYTVjYy1jMzYwNjI3NzYxM2YiLCJvcmdJZCI6IjA1ODQxMjRkLWE1OTgtNDkzYi04ZGM2LTM1ZDRiOGRiZDJiYyIsIm9yZ05hbWUiOiJSLiBOLiBHLiBQYXRlbCBJbnN0aXR1dGUgT2YgVGVjaG5vbG9neSIsIm9yZ05hbWVTaG9ydCI6IlJOR1BJVCIsIm9yZ0xvY2F0aW9uIjoiUk5HUElULCBCYXJkb2xpLCBHdWphcmF0LCBJbmRpYSIsIm9yZ0NpdHkiOiJCYXJkb2xpIiwicGxhbnRDYXBhY2l0eSI6IjEyMCBLd2giLCJwbGFudE51bWJlck9mUGFuZWxzIjoiMTgwIiwidXNlck5hbWUiOiJEZXYgVXNlciIsInVzZXJFbWFpbCI6ImRldjAwQHBhbmVsaXRlLmNvbSIsInVzZXJNb2JpbGUiOiIrOTE4KioqKiowMzIzIn0='
            }})

    except Exception as error:
        print(error)
        return jsonify({'status': 'failure', 'errorMsg': 'Invalid payload format'})

# Run the app if this script is executed
if __name__ == '__main__':
    app.run(API_HOST, API_PORT, debug=config.get('IS_DEVELOPMENT'))
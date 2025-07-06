import os
import datetime
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Load secrets from Replit environment
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
TENANT_ID = os.environ.get("TENANT_ID")

# Token endpoint for Microsoft Graph API
token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

# Generate access token
def get_access_token():
    token_data = {
        'client_id': CLIENT_ID,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    token_response = requests.post(token_url, data=token_data)
    return token_response.json().get("access_token")

# Main calendar route
@app.route('/calendar/today')
def get_todays_events():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id query parameter"}), 400

    access_token = get_access_token()
    if not access_token:
        return jsonify({"error": "Failed to obtain access token"}), 500

    now = datetime.datetime.utcnow()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    end = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "startDateTime": start,
        "endDateTime": end
    }

    calendar_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/calendarview"
    response = requests.get(calendar_url, headers=headers, params=params)

    if response.status_code != 200:
        return jsonify({"error": "Graph API call failed", "details": response.json()}), response.status_code

    return jsonify(response.json())

@app.route('/')
def hello():
    return 'Outlook Calendar API is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

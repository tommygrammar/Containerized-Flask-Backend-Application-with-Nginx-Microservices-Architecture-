from flask import Flask, request, jsonify
import requests
import firebase_admin
from firebase_admin import credentials, auth
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("/app/security_key.json")
firebase_admin.initialize_app(cred)

connection_established = False

def establish_connection():
    global connection_established
    connection_established = True
    print("Connection established")

def paralyze_connection():
    global connection_established
    connection_established = False
    print("Connection paralyzed")

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    sign_in_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDpxKOWUxontyYOUGRgh9zZ1juyOE0hQoQ"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    r = requests.post(sign_in_url, json=payload)
    if r.status_code == 200:
        establish_connection()
        return jsonify({"message": "Successfully authenticated"}), 200
    else:
        paralyze_connection()
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"connection_established": connection_established})

if __name__ == '__main__':
    app.run(port=5000, host = "0.0.0.0", debug=True)

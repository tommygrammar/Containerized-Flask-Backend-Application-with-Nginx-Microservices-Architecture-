from flask import Flask, request, jsonify
import json
import os
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_FILE = '/app/database.json'
RULES_FILE = '/app/rules.json'

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

database = load_json(DATABASE_FILE)
rules = load_json(RULES_FILE)

def check_permissions(uid, collection, action, document=None):
    user_rules = rules.get(uid, {})
    if collection not in user_rules:
        return False
    if action == 'write':
        return user_rules[collection].get('allow_write', False)
    if document and document not in user_rules[collection]:
        return False
    return True

@app.route('/write', methods=['POST'])
def write_structure():
    auth_status = requests.get('http://auth:5000/status').json()
    if not auth_status['connection_established']:
        return jsonify({"error": "Connection not established"}), 403

    data = request.json
    uid = data.get('uid')
    main_collection = data.get('main_collection')
    document = data.get('document')
    fields = data.get('fields', {})

    if not check_permissions(uid, main_collection, 'write', document):
        return jsonify({"error": "Write access is not allowed"}), 403

    db = load_json(DATABASE_FILE)
    if main_collection not in db:
        db[main_collection] = {}
    if document not in db[main_collection]:
        db[main_collection][document] = {}

    for field, content in fields.items():
        if content:
            db[main_collection][document][field] = content

    save_json(db, DATABASE_FILE)
    message = {'collection': main_collection, 'document': document, **fields}
    requests.post('http://message:5004/publish', json=message)
    
    return jsonify({"message": "Data successfully written."}), 200

if __name__ == '__main__':
    app.run(port=5002, host = "0.0.0.0", debug=True)

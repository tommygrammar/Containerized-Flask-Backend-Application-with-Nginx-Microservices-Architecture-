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

database = load_json(DATABASE_FILE)
rules = load_json(RULES_FILE)

def check_permissions(uid, collection, action, document=None, field=None):
    user_rules = rules.get(uid, {})
    if collection not in user_rules:
        return False
    if action == 'read':
        return user_rules[collection].get('allow_read', False)
    if document and document not in user_rules[collection]:
        return False
    if field and field not in user_rules[collection].get(document, {}):
        return False
    return True

@app.route('/read', methods=['POST'])
def read_structure():
    auth_status = requests.get('http://auth:5000/status').json()
    if not auth_status['connection_established']:
        return jsonify({"error": "Connection not established"}), 403

    data = request.json
    uid = data.get('uid')
    main_collection = data.get('main_collection')
    document = data.get('document')
    field = data.get('field')

    if not check_permissions(uid, main_collection, 'read', document, field):
        return jsonify({"error": "Read access is not allowed"}), 403

    db = load_json(DATABASE_FILE)
    if main_collection not in db:
        return jsonify({"error": f"Main collection '{main_collection}' does not exist."}), 404

    if document:
        if document not in db[main_collection]:
            return jsonify({"error": f"Document '{document}' does not exist."}), 404
        if field:
            if field not in db[main_collection][document]:
                return jsonify({"error": f"Field '{field}' does not exist."}), 404
            return jsonify({field: db[main_collection][document][field]}), 200
        return jsonify(db[main_collection][document]), 200

    return jsonify(db[main_collection]), 200

if __name__ == '__main__':
    app.run(port=5001, host = "0.0.0.0", debug=True)

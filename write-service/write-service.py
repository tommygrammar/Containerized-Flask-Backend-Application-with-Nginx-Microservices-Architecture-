from flask import Flask, request, jsonify
import requests
import redis
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.route('/write', methods=['POST'])
def write_structure():
    auth_status = requests.get('http://auth:5000/status').json()
    if not auth_status['connection_established']:
        return jsonify({"error": "Connection not established"}), 403

    data = request.json
    uid = data.get('uid')
    collection = data.get('collection')
    document = data.get('document')
    fields = data.get('fields', {})

    if not collection or not document or not fields:
        return jsonify({"error": "Main collection, document, and fields are required."}), 400

    for field, content in fields.items():
        if content is not None:
            redis_client.hset(f"{collection}:{document}", field, content)

    message = {'collection': collection, 'document': document, **fields}
    requests.post('http://websocket:5003/publish', json=message)
    
    return jsonify({"message": "Data successfully written."}), 200

if __name__ == '__main__':
    app.run(port=5002, host="0.0.0.0", debug=True)
